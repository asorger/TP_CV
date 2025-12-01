import cv2
import numpy as np
import config as cfg

def ensure_canvas(h, w):
    if cfg.canvas is None:
        cfg.canvas = np.zeros((h, w, 3), np.uint8)
    return cfg.canvas

def draw_brush(x, y):
    cv2.circle(cfg.canvas, (x, y), cfg.thickness, cfg.current_color, -1)

def erase_at(x, y):
    cv2.circle(cfg.canvas, (x, y), cfg.erase_thickness, (0, 0, 0), -1)

def spray_at(x, y):
    for i in range(20):
        dx = np.random.randint(-20, 20)
        dy = np.random.randint(-20, 20)
        cv2.circle(cfg.canvas, (x + dx, y + dy), 2, cfg.current_color, -1)
        
def clear_canvas():
    cfg.canvas[:] = 0

def undo():
    if cfg.history:
        cfg.canvas[:] = cfg.history.pop().copy()