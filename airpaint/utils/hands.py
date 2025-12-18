import mediapipe as mp
import cv2

# Referência ao módulo de deteção de mãos do MediaPipe.
mp_hands = mp.solutions.hands

# Instância do detector de mãos:
# - max_num_hands=2: deteta até duas mãos em simultâneo
# - min_detection_confidence=0.7: confiança mínima para a deteção inicial
# - min_tracking_confidence=0.6: confiança mínima para o tracking entre frames
hands = mp_hands.Hands(
    max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.6
)


def detect_hands(frame):
    """
    Deteta mãos num frame e devolve informação útil para interação (landmarks e posição).

    O que faz:
    - Converte o frame BGR -> RGB (MediaPipe espera RGB).
    - Corre o modelo Hands do MediaPipe.
    - Se existirem mãos detetadas:
      - para cada mão, extrai os landmarks (lista de pontos)
      - calcula a posição (x, y) do landmark 8 (ponta do dedo indicador) em pixels
      - identifica se a mão é "Left" ou "Right" com base no multi_handedness
      - guarda separadamente: landmarks, objeto completo da mão e posição

    Retorno:
    - frame: o frame original (não é alterado aqui)
    - left_lm: lista de landmarks (normalizados) da mão esquerda, ou None
    - right_lm: lista de landmarks (normalizados) da mão direita, ou None
    - left_pos: (x, y) em pixels da ponta do indicador da mão esquerda, ou None
    - right_pos: (x, y) em pixels da ponta do indicador da mão direita, ou None
    - left_hand_obj: objeto do MediaPipe com a mão esquerda (para desenhar landmarks), ou None
    - right_hand_obj: objeto do MediaPipe com a mão direita (para desenhar landmarks), ou None
    """
    # Dimensões do frame (altura e largura)
    h, w, _ = frame.shape

    # Conversão para RGB para processamento pelo MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processa o frame para deteção de mãos
    results = hands.process(rgb)

    # Inicializa as variáveis de saída como None (caso não haja deteções)
    left_lm = None
    right_lm = None
    left_hand_obj = None
    right_hand_obj = None
    left_pos = None
    right_pos = None

    # Se houver landmarks de mãos detetadas
    if results.multi_hand_landmarks:
        # Percorre cada mão detetada
        for idx, handLms in enumerate(results.multi_hand_landmarks):
            # Lista de landmarks (21 pontos) com coordenadas normalizadas (0..1)
            lm = handLms.landmark

            # Converte a posição do landmark 8 (ponta do indicador) para coordenadas em pixels
            x = int(lm[8].x * w)
            y = int(lm[8].y * h)

            # Determina se a mão é esquerda ou direita (label "Left" ou "Right")
            hand_label = results.multi_handedness[idx].classification[0].label

            # Guarda dados da mão esquerda
            if hand_label == "Left":
                left_lm = lm
                left_hand_obj = handLms
                left_pos = (x, y)

            # Caso contrário, assume mão direita e guarda dados
            else:
                right_lm = lm
                right_hand_obj = handLms
                right_pos = (x, y)

    # Devolve o frame e toda a informação recolhida
    return frame, left_lm, right_lm, left_pos, right_pos, left_hand_obj, right_hand_obj