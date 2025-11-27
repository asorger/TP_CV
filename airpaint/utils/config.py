import numpy as np

canvas = None

thickness = 10
erase_thickness = 20

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