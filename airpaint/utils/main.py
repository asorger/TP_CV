import cv2
import numpy as np

from gestures import (
    one_finger,
    pinch,
    three_fingers,
    two_fingers,
    is_fist,
    four_fingers,
)
from hands import process_hands
from drawing import ensure_canvas, erase_point, draw_point, spray
import config as cfg

cap = cv2.VideoCapture(0)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    cfg.canvas = ensure_canvas(h, w)

    frame, left_lm, right_lm, left_pos, right_pos = process_hands(frame, w, h)

    # ================= Ferramentas mão esquerda =================
    if left_lm:
        if one_finger(left_lm):
            cfg.color_index = (cfg.color_index + 1) % len(cfg.colors)
            cfg.current_color = cfg.colors[cfg.color_index]

        if pinch(left_lm):
            cfg.spray_mode = True
        else:
            cfg.spray_mode = False

        if three_fingers(left_lm):
            cfg.thickness = min(60, cfg.thickness + 1)

        if two_fingers(left_lm):
            cfg.thickness = max(2, cfg.thickness - 1)

    # ================= Mão direita =================
    if right_lm and right_pos:
        x, y = right_pos

        if is_fist(left_lm) and four_fingers(right_lm):
            erase_point(x, y)

        elif pinch(right_lm):
            if cfg.spray_mode:
                spray(x, y)
            else:
                draw_point(x, y)

    output = cv2.add(frame, cfg.canvas)

    cv2.imshow("AirPaint — Modular", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
