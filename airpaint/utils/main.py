import cv2
import time
import os

import mediapipe as mp

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
from yolo_detector import detect_book, detect_can
from face import detect_smile

right_arm_start = None
left_arm_start = None
ARM_HOLD_TIME = 4

select_start = None
selected_index = None

last_color_change = 0
COLOR_DELAY = 0.6

book_start = None
BOOK_HOLD_TIME = 3

if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

mp_draw = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

cap = cv2.VideoCapture(0)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    raw_frame = frame.copy()
    debug_frame = raw_frame.copy()

    h, w, _ = frame.shape

    # POSE
    right_up, left_up, pose_lms = detect_pose(frame)

    ensure_canvas(h, w)

    # MÃOS
    frame, left_lm, right_lm, left_pos, right_pos, left_hand_obj, right_hand_obj = (
        detect_hands(frame)
    )

    draw_palette(frame)

    # FACE / SMILE
    smiling, face_lms = detect_smile(frame)

    if smiling:
        cfg.rainbow_mode = True
    else:
        cfg.rainbow_mode = False

    if cfg.rainbow_mode:
        now = time.time()
        if now - cfg.last_rainbow_switch >= cfg.rainbow_delay:
            cfg.color_index = (cfg.color_index + 1) % len(cfg.colors)
            cfg.current_color = cfg.colors[cfg.color_index]
            cfg.last_rainbow_switch = now

    if left_pos:
        idx = check_palette_selection(left_pos[0], left_pos[1], h)
        if idx is not None:
            if selected_index != idx:
                selected_index = idx
                select_start = time.time()
            else:
                if time.time() - select_start >= 1.8:
                    cfg.current_color = cfg.colors[idx]
        else:
            selected_index = None
            select_start = None

    if left_lm and not cfg.rainbow_mode:
        if one_finger(left_lm):
            now = time.time()
            if now - last_color_change >= COLOR_DELAY:
                cfg.color_index = (cfg.color_index + 1) % len(cfg.colors)
                cfg.current_color = cfg.colors[cfg.color_index]
                last_color_change = now

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

    # YOLO – LIVRO
    book_detected = detect_book(raw_frame)

    if book_detected:
        left_lm = None
        right_lm = None
        left_pos = None
        right_pos = None
        cfg.spray_mode = False
        cfg.rainbow_mode = False

        if book_start is None:
            book_start = time.time()
        else:
            if time.time() - book_start >= BOOK_HOLD_TIME:
                filename = f"screenshots/airpaint_{int(time.time())}.png"
                output = cv2.add(frame, cfg.canvas)
                cv2.imwrite(filename, output)

                print("Screenshot salva:", filename)
                book_start = None
    else:
        book_start = None

    # YOLO – LATA
    can_detected = detect_can(raw_frame)
    if can_detected:
        cfg.spray_mode = True

    # ========== DEBUG DRAW ==========

    # Pose (esqueleto)
    if pose_lms:
        mp_draw.draw_landmarks(
            debug_frame,
            pose_lms,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2),
        )

    # Mãos
    if left_hand_obj is not None:
        mp_draw.draw_landmarks(
            debug_frame,
            left_hand_obj,
            mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2),
        )

    if right_hand_obj is not None:
        mp_draw.draw_landmarks(
            debug_frame,
            right_hand_obj,
            mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
        )

    # Face mesh
    if face_lms is not None:
        mp_draw.draw_landmarks(
            debug_frame,
            face_lms,
            mp_face_mesh.FACEMESH_TESSELATION,
            mp_draw.DrawingSpec(color=(255, 0, 255), thickness=1, circle_radius=1),
            mp_draw.DrawingSpec(color=(0, 255, 255), thickness=1),
        )

    # Texto debug – smile, book, can
    if smiling:
        cv2.putText(
            debug_frame,
            "SMILE",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 255),
            2,
        )

    if book_detected:
        cv2.putText(
            debug_frame, "BOOK", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2
        )

    if can_detected:
        cv2.putText(
            debug_frame, "CAN", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )

    # ================================

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
    cv2.imshow("Debug View", debug_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
