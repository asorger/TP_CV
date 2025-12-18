import cv2
import numpy as np
import config as cfg

def ensure_canvas(h, w):
    """
    Garante que o canvas existe e tem as dimensões corretas.

    - Se cfg.canvas ainda não tiver sido inicializado (None), cria um canvas preto
      com tamanho (h, w) e 3 canais (BGR), tipo uint8 (formato típico do OpenCV).
    - Devolve sempre cfg.canvas (o canvas atual).
    """
    if cfg.canvas is None:
        cfg.canvas = np.zeros((h, w, 3), np.uint8)
    return cfg.canvas

def draw_brush(x, y):
    """
    Desenha no canvas usando um pincel circular.

    - Desenha um círculo preenchido (-1) no cfg.canvas na posição (x, y).
    - O raio é cfg.thickness.
    - A cor usada é cfg.current_color (em BGR).
    """
    cv2.circle(cfg.canvas, (x, y), cfg.thickness, cfg.current_color, -1)

def erase_at(x, y):
    """
    Apaga no canvas simulando uma borracha.

    - Desenha um círculo preenchido (-1) na cor preta (0,0,0) na posição (x, y).
    - O raio é cfg.erase_thickness (normalmente maior do que o pincel).
    """
    cv2.circle(cfg.canvas, (x, y), cfg.erase_thickness, (0, 0, 0), -1)

def spray_at(x, y):
    """
    Modo spray: desenha vários pontos aleatórios à volta do ponto (x, y).

    - Faz 20 iterações, gerando offsets aleatórios dx/dy no intervalo [-20, 20).
    - Em cada iteração desenha um pequeno círculo (raio 2) com cfg.current_color.
    - Cria um efeito de "spray" (pontos dispersos).
    """
    for i in range(20):
        dx = np.random.randint(-20, 20)
        dy = np.random.randint(-20, 20)
        cv2.circle(cfg.canvas, (x + dx, y + dy), 2, cfg.current_color, -1)

def clear_canvas():
    """
    Limpa o canvas totalmente.

    - Define todos os pixels do cfg.canvas para 0 (preto) usando slicing.
    - Mantém as dimensões e o objeto canvas, apenas zera o conteúdo.
    """
    cfg.canvas[:] = 0

def undo():
    """
    Desfaz a última ação, restaurando o estado anterior do canvas.

    - Se cfg.history tiver estados guardados:
      - retira (pop) o último estado do histórico
      - copia-o para o cfg.canvas atual (cfg.canvas[:] = ...)
    - Usa .copy() para garantir independência de memória.
    """
    if cfg.history:
        cfg.canvas[:] = cfg.history.pop().copy()

def draw_palette(frame):
    """
    Desenha a paleta de cores sobre um 'frame' (imagem de visualização).

    - Divide a altura do frame em blocos verticais, um por cada cor em cfg.colors.
    - Desenha retângulos preenchidos (paleta) numa coluna fixa à esquerda (largura 60px).
    - Se a cor do bloco for a cfg.current_color, desenha uma borda branca para destacar.
    """
    h = frame.shape[0]
    box_h = h // len(cfg.colors)
    box_w = 60
    for i, col in enumerate(cfg.colors):
        y1 = i * box_h
        y2 = y1 + box_h
        cv2.rectangle(frame, (0, y1), (box_w, y2), col, -1)
        if col == cfg.current_color:
            cv2.rectangle(frame, (0, y1), (box_w, y2), (255,255,255), 3)

def check_palette_selection(x, y, h):
    """
    Verifica se o utilizador clicou/selecionou uma cor da paleta.

    Parâmetros:
    - x, y: coordenadas do clique/ponto (normalmente do dedo/mouse).
    - h: altura total da área usada para calcular os blocos (normalmente frame.shape[0]).

    Regras:
    - Se x > 60, está fora da área da paleta (a paleta ocupa 60px à esquerda) → devolve None.
    - Caso contrário:
      - calcula a altura de cada bloco (box_h)
      - devolve o índice da cor selecionada (y // box_h)
        (índice para usar diretamente em cfg.colors).
    """
    if x > 60:
        return None
    box_h = h // len(cfg.colors)
    return y // box_h