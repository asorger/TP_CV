import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

def detect_hands(frame):
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    left_lm = None
    right_lm = None
    left_pos = None
    right_pos = None

    if results.multi_hand_landmarks:
        for idx, handLms in enumerate(results.multi_hand_landmarks):
            lm = handLms.landmark
            x = int(lm[8].x * w)
            y = int(lm[8].y * h)

            hand_label = results.multi_handedness[idx].classification[0].label

            if hand_label == "Left":
                left_lm = lm
                left_pos = (x, y)
                mp_draw.draw_landmarks(
                    frame,
                    handLms,
                    mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3),
                    mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )
            else:
                right_lm = lm
                right_pos = (x, y)
                mp_draw.draw_landmarks(
                    frame,
                    handLms,
                    mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
                )

    return frame, left_lm, right_lm, left_pos, right_pos