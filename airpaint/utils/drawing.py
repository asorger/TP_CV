import cv2
import numpy as np
from config import canvas, current_color, thickness, erase_thickness

def ensure_canvas(h, w):
    global canvas
    if canvas is None:
        canvas = np.zeros((h, w, 3), np.uint8)
    return canvas

def draw_point(x, y):
    cv2.circle(canvas, (x, y), thickness, current_color, -1)

def erase_point(x, y):
    cv2.circle(canvas, (x, y), erase_thickness, (0, 0, 0), -1)

def spray(x, y):
    for i in range(20):
        dx = np.random.randint(-20, 20)
        dy = np.random.randint(-20, 20)
        cv2.circle(canvas, (x + dx, y + dy), 2, current_color, -1)