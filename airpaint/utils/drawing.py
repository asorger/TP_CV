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


def draw_palette(frame):
    h = frame.shape[0]
    box_h = h // len(cfg.colors)
    box_w = 60
    for i, col in enumerate(cfg.colors):
        y1 = i * box_h
        y2 = y1 + box_h
        cv2.rectangle(frame, (0, y1), (box_w, y2), col, -1)
        if col == cfg.current_color:
            cv2.rectangle(frame, (0, y1), (box_w, y2), (255, 255, 255), 3)


def check_palette_selection(x, y, h):
    if x > 60:
        return None
    box_h = h // len(cfg.colors)
    return y // box_hdrawing.py


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


def draw_palette(frame):
    h = frame.shape[0]
    box_h = h // len(cfg.colors)
    box_w = 60
    for i, col in enumerate(cfg.colors):
        y1 = i * box_h
        y2 = y1 + box_h
        cv2.rectangle(frame, (0, y1), (box_w, y2), col, -1)
        if col == cfg.current_color:
            cv2.rectangle(frame, (0, y1), (box_w, y2), (255, 255, 255), 3)


def check_palette_selection(x, y, h):
    if x > 60:
        return None
    box_h = h // len(cfg.colors)
    return y // box_h
