import cv2
import time
import os

import mediapipe as mp

import config as cfg
from gestures import (
    one_finger,
    two_fingers,
    three_fingers,
    four_fingers,
    pinch,
    is_fist,
)
from hands import detect_hands
from drawing import (
    ensure_canvas,
    draw_brush,
    erase_at,
    spray_at,
    draw_palette,
    check_palette_selection,
)
from drawing import clear_canvas, undo
from pose import detect_pose
from yolo_detector import detect_book, detect_can
from face import detect_smile

from tool_window import ToolWindow

# ============================
# Variáveis de controlo (gestos / timers)
# ============================

# Controlam o "hold" do braço (pose) para limpar / fazer undo
right_arm_start = None
left_arm_start = None
ARM_HOLD_TIME = 4  # segundos que o braço tem de estar levantado para disparar ação

# Controlam a seleção de uma cor na paleta (segurar o dedo em cima de uma cor)
select_start = None
selected_index = None

# Controlo de delay para trocar cor ao fazer 1 dedo (evita trocar demasiado rápido)
last_color_change = 0
COLOR_DELAY = 0.6  # segundos

# Controla o "hold" do livro detetado por YOLO para tirar screenshot
book_start = None
BOOK_HOLD_TIME = 3  # segundos com o livro visível para disparar print

# Pasta onde serão guardados os screenshots do desenho
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# ============================
# Atalhos para módulos MediaPipe (usados no modo debug)
# ============================
mp_draw = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

# ============================
# Inicialização da câmara
# ============================
cap = cv2.VideoCapture(0)

# Janela/engine para animação visual do "tool" atual (brush/spray/eraser)
tool_window = ToolWindow()

# Tool atual guardado em config (estado global do sistema)
cfg.current_tool = "brush"

# ============================
# Loop principal
# ============================
while True:
    ok, frame = cap.read()
    if not ok:
        break

    # Espelha o vídeo (efeito espelho para ser mais intuitivo ao desenhar)
    frame = cv2.flip(frame, 1)

    # Cópias do frame:
    # - raw_frame: para deteções (YOLO/pose/face) sem overlay do canvas
    # - debug_frame: para desenhar landmarks e visualizar diagnóstico
    raw_frame = frame.copy()
    debug_frame = raw_frame.copy()

    # Dimensões do frame
    h, w, _ = frame.shape

    # ============================
    # POSE (braços levantados)
    # ============================
    # detect_pose devolve:
    # - right_up: True se braço direito estiver levantado
    # - left_up: True se braço esquerdo estiver levantado
    # - pose_lms: landmarks da pose (para debug)
    right_up, left_up, pose_lms = detect_pose(frame)

    # Garante que existe um canvas do tamanho do frame
    ensure_canvas(h, w)

    # ============================
    # MÃOS (landmarks + posição do indicador)
    # ============================
    # detect_hands devolve:
    # - left_lm/right_lm: landmarks normalizados das mãos (listas)
    # - left_pos/right_pos: posição (x,y) em pixels do dedo indicador (landmark 8)
    # - left_hand_obj/right_hand_obj: objetos MediaPipe para desenhar landmarks (debug)
    frame, left_lm, right_lm, left_pos, right_pos, left_hand_obj, right_hand_obj = (
        detect_hands(frame)
    )

    # Desenha a paleta de cores na lateral esquerda do frame
    draw_palette(frame)

    # ============================
    # FACE / SMILE -> Rainbow Mode
    # ============================
    # detect_smile devolve:
    # - smiling: True se sorriso estiver confirmado por vários frames
    # - face_lms: landmarks da face (para debug)
    smiling, face_lms = detect_smile(frame)

    # Se estiver a sorrir, ativa o modo arco-íris (troca automática de cor)
    cfg.rainbow_mode = smiling

    # Troca de cor automática no modo rainbow com base num delay
    if cfg.rainbow_mode:
        now = time.time()
        if now - cfg.last_rainbow_switch >= cfg.rainbow_delay:
            cfg.color_index = (cfg.color_index + 1) % len(cfg.colors)
            cfg.current_color = cfg.colors[cfg.color_index]
            cfg.last_rainbow_switch = now

    # ============================
    # Seleção de cor com a mão esquerda (hover/hold na paleta)
    # ============================
    # Se existir posição da mão esquerda (indicador)
    if left_pos:
        # check_palette_selection devolve índice da cor se estiver na zona da paleta, senão None
        idx = check_palette_selection(left_pos[0], left_pos[1], h)
        if idx is not None:
            # Se mudou o índice selecionado, reinicia o timer do "hold"
            if selected_index != idx:
                selected_index = idx
                select_start = time.time()
            else:
                # Se mantém na mesma cor durante >= 1.8s, confirma seleção
                if time.time() - select_start >= 1.8:
                    cfg.current_color = cfg.colors[idx]
        else:
            # Fora da paleta: reseta seleção
            selected_index = None
            select_start = None

    # ============================
    # Gestos da mão esquerda (controlos de cor, spray e espessura)
    # ============================
    # Só processa estes gestos se há mão esquerda e o rainbow_mode estiver desligado
    if left_lm and not cfg.rainbow_mode:
        # 1 dedo: trocar cor ciclicamente com um delay (para não trocar em loop demasiado rápido)
        if one_finger(left_lm):
            now = time.time()
            if now - last_color_change >= COLOR_DELAY:
                cfg.color_index = (cfg.color_index + 1) % len(cfg.colors)
                cfg.current_color = cfg.colors[cfg.color_index]
                last_color_change = now

        # Pinch (polegar+indicador): ativa modo spray e altera ferramenta atual
        if pinch(left_lm):
            cfg.spray_mode = True
            cfg.current_tool = "spray"
        else:
            cfg.spray_mode = False
            cfg.current_tool = "brush"

        # 3 dedos: aumenta espessura do pincel (com limite máximo)
        if three_fingers(left_lm):
            cfg.thickness = min(60, cfg.thickness + 1)

        # 2 dedos: diminui espessura do pincel (com limite mínimo)
        if two_fingers(left_lm):
            cfg.thickness = max(2, cfg.thickness - 1)

    # ============================
    # Ações da mão direita (desenhar/apagar)
    # ============================
    if right_lm and right_pos:
        x, y = right_pos

        # Combinação: punho na esquerda + 4 dedos na direita -> borracha
        if is_fist(left_lm) and four_fingers(right_lm):
            cfg.current_tool = "eraser"
            erase_at(x, y)

        # Pinch na direita -> desenhar (brush ou spray)
        elif pinch(right_lm):
            # Guarda estado antes de desenhar para permitir undo
            cfg.save_state(cfg.canvas)
            if cfg.spray_mode:
                spray_at(x, y)
            else:
                draw_brush(x, y)

    # ============================
    # YOLO – LIVRO (tirar screenshot)
    # ============================
    # Se o livro for detetado:
    # - bloqueia controlos (mãos/spray/rainbow) para evitar interferência
    # - inicia um timer; se durar >= BOOK_HOLD_TIME, grava imagem composta (frame + canvas)
    book_detected = detect_book(raw_frame)
    if book_detected:
        left_lm = right_lm = None
        left_pos = right_pos = None
        cfg.spray_mode = False
        cfg.rainbow_mode = False

        if book_start is None:
            book_start = time.time()
        else:
            if time.time() - book_start >= BOOK_HOLD_TIME:
                filename = f"screenshots/airpaint_{int(time.time())}.png"
                cv2.imwrite(filename, cv2.add(frame, cfg.canvas))
                book_start = None
    else:
        # Se o livro desaparecer, reseta o timer
        book_start = None

    # ============================
    # YOLO – LATA (forçar spray)
    # ============================
    # Se a lata for detetada, ativa spray e muda a ferramenta para spray
    if detect_can(raw_frame):
        cfg.spray_mode = True
        cfg.current_tool = "spray"

    # ============================
    # DEBUG: desenhar landmarks no debug_frame
    # ============================

    # Pose landmarks (se existirem)
    if pose_lms:
        mp_draw.draw_landmarks(
            debug_frame,
            pose_lms,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2),
        )

    # Mão esquerda (se existir)
    if left_hand_obj is not None:
        mp_draw.draw_landmarks(
            debug_frame,
            left_hand_obj,
            mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2),
        )

    # Mão direita (se existir)
    if right_hand_obj is not None:
        mp_draw.draw_landmarks(
            debug_frame,
            right_hand_obj,
            mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
        )

    # Face landmarks (se existirem)
    if face_lms is not None:
        mp_draw.draw_landmarks(
            debug_frame,
            face_lms,
            mp_face_mesh.FACEMESH_TESSELATION,
            mp_draw.DrawingSpec(color=(255, 0, 255), thickness=1, circle_radius=1),
            mp_draw.DrawingSpec(color=(0, 255, 255), thickness=1),
        )

    # ============================
    # Ações por pose (braço levantado com hold)
    # ============================

    # Braço direito levantado: limpar canvas após ARM_HOLD_TIME
    if right_up:
        if right_arm_start is None:
            right_arm_start = time.time()
        else:
            if time.time() - right_arm_start >= ARM_HOLD_TIME:
                clear_canvas()
                right_arm_start = None
    else:
        right_arm_start = None

    # Braço esquerdo levantado: undo após ARM_HOLD_TIME
    if left_up:
        if left_arm_start is None:
            left_arm_start = time.time()
        else:
            if time.time() - left_arm_start >= ARM_HOLD_TIME:
                undo()
                left_arm_start = None
    else:
        left_arm_start = None

    # ============================
    # Composição final e janelas de visualização
    # ============================
    # output = frame com paleta + canvas desenhado por cima
    output = cv2.add(frame, cfg.canvas)

    # Janelas:
    # - AirPaint: resultado final
    # - Debug View: landmarks e diagnóstico
    # - Tool Animation: animação/ícone da ferramenta atual
    cv2.imshow("AirPaint 3D — Versao Modular", output)
    cv2.imshow("Debug View", debug_frame)
    cv2.imshow("Tool Animation", tool_window.get_frame(cfg.current_tool))

    # Tecla 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ============================
# Cleanup
# ============================
cap.release()
cv2.destroyAllWindows()