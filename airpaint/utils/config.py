import numpy as np

# Canvas principal onde vais desenhar (normalmente um array NumPy com a imagem)
canvas = None

# Espessura do pincel (em pixels) para desenhar normalmente
thickness = 10

# Espessura da borracha (em pixels) — normalmente maior para apagar mais rápido
erase_thickness = 40

# Histórico de estados do canvas para permitir "undo"
history = []

# Limite de estados guardados no histórico (para não gastar demasiada RAM)
MAX_HISTORY = 20

# Paleta de cores (BGR, como o OpenCV usa por defeito: Blue, Green, Red)
colors = [
    (255, 0, 0),      # Vermelho
    (255, 64, 0),     # Laranja forte
    (255, 128, 0),    # Laranja
    (255, 191, 0),    # Amarelo alaranjado
    (255, 255, 0),    # Amarelo
    (191, 255, 0),    # Lima claro
    (128, 255, 0),    # Lima
    (64, 255, 0),     # Verde-lima
    (0, 255, 0),      # Verde
    (0, 255, 64),     # Verde-água
    (0, 255, 128),    # Turquesa
    (0, 255, 191),    # Ciano claro
    (0, 255, 255),    # Ciano
    (0, 191, 255),    # Azul-ciano
    (0, 128, 255),    # Azul claro
    (0, 64, 255),     # Azul forte
    (0, 0, 255),      # Azul
    (64, 0, 255),     # Roxo
    (128, 0, 255),    # Violeta
    (191, 0, 255)     # Magenta/rosa-violeta
]

# Índice atual da cor selecionada na lista "colors"
color_index = 0

# Cor atual (tuple BGR) usada para desenhar
current_color = colors[color_index]

# Modo spray: quando True, em vez de linha contínua faz "pontos" tipo spray
spray_mode = False

# Modo arco-íris: quando True, vai trocando a cor automaticamente ao longo do tempo
rainbow_mode = False

# Tempo mínimo (em segundos) entre trocas de cor no modo arco-íris
rainbow_delay = 0.25

# Guarda o último instante em que a cor foi trocada no modo arco-íris
last_rainbow_switch = 0

def save_state(canvas):
    """
    Guarda um 'snapshot' do canvas no histórico (para suportar undo).

    Regras:
    - Mantém o histórico com no máximo MAX_HISTORY estados.
    - Guarda sempre uma CÓPIA do canvas (canvas.copy()) para evitar que alterações futuras
      modifiquem o estado guardado.
    """
    # Se o histórico já estiver cheio, remove o estado mais antigo (posição 0)
    if len(history) >= MAX_HISTORY:
        history.pop(0)

    # Adiciona o estado atual do canvas como cópia independente
    history.append(canvas.copy())