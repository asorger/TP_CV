import cv2

import config as cfg
from gestures import (
    one_finger,
    two_fingers,
    three_fingers,
    four_fingers,
    pinch,
    is_fist
)
from hands import detect_hands
from drawing import ensure_canvas, draw_brush, erase_at, spray_at

cap = cv2.VideoCapture(0)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    ensure_canvas(h, w)

    frame, left_lm, right_lm, left_pos, right_pos = detect_hands(frame)

    # ================= MÃO ESQUERDA (Ferramentas) =================
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

    if right_lm and right_pos:
        x, y = right_pos

        if is_fist(left_lm) and four_fingers(right_lm):
            erase_at(x, y)

        elif pinch(right_lm):
            if cfg.spray_mode:
                spray_at(x, y)
            else:
                draw_brush(x, y)

    output = cv2.add(frame, cfg.canvas)

    cv2.imshow("AirPaint 3D — Versao Modular", output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()