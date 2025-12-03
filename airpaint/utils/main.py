import cv2
import time

import config as cfg
from gestures import (
    one_finger,
    two_fingers,
    three_fingers,
    four_fingers,
    pinch,
    is_fist,
)
from hands import detect_hands
from drawing import (
    ensure_canvas,
    draw_brush,
    erase_at,
    spray_at,
    draw_palette,
    check_palette_selection,
)
from drawing import clear_canvas, undo
from pose import detect_pose

right_arm_start = None
left_arm_start = None
ARM_HOLD_TIME = 4

select_start = None
selected_index = None

cap = cv2.VideoCapture(0)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    right_up, left_up = detect_pose(frame)

    ensure_canvas(h, w)

    frame, left_lm, right_lm, left_pos, right_pos = detect_hands(frame)

    draw_palette(frame)

    if left_pos:
        idx = check_palette_selection(left_pos[0], left_pos[1], h)
        if idx is not None:
            if selected_index != idx:
                selected_index = idx
                select_start = time.time()
            else:
                if time.time() - select_start >= 0.6:
                    cfg.current_color = cfg.colors[idx]
        else:
            selected_index = None
            select_start = None

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
            cfg.save_state(cfg.canvas)

            if cfg.spray_mode:
                spray_at(x, y)
            else:
                draw_brush(x, y)

    if right_up:
        if right_arm_start is None:
            right_arm_start = time.time()
        else:
            elapsed = time.time() - right_arm_start
            if elapsed >= ARM_HOLD_TIME:
                clear_canvas()
                right_arm_start = None
    else:
        right_arm_start = None

    if left_up:
        if left_arm_start is None:
            left_arm_start = time.time()
        else:
            elapsed = time.time() - left_arm_start
            if elapsed >= ARM_HOLD_TIME:
                undo()
                left_arm_start = None
    else:
        left_arm_start = None

    output = cv2.add(frame, cfg.canvas)

    cv2.imshow("AirPaint 3D — Versao Modular", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
