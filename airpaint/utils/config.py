import numpy as np

canvas = None

thickness = 10
erase_thickness = 40
history = []
MAX_HISTORY = 20

colors = [
    (0, 255, 0),   
    (255, 0, 0),   
    (0, 0, 255),
    (0, 255, 255), 
    (255, 0, 255), 
    (255, 255, 255)
]

color_index = 0
current_color = colors[color_index]

spray_mode = False

def save_state(canvas):
    if len(history) >= MAX_HISTORY:
        history.pop(0)
    history.append(canvas.copy())