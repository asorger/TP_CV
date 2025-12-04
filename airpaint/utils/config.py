import numpy as np

canvas = None

thickness = 10
erase_thickness = 40
history = []
MAX_HISTORY = 20

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

color_index = 0
current_color = colors[color_index]

spray_mode = False

rainbow_mode = False
rainbow_delay = 0.25    
last_rainbow_switch = 0

def save_state(canvas):
    if len(history) >= MAX_HISTORY:
        history.pop(0)
    history.append(canvas.copy())