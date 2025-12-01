import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

LEFT_COLOR = (0, 0, 255)
RIGHT_COLOR = (0, 255, 0) 

def draw_colored_hand(frame, handLms, color):
    for conn in mp_hands.HAND_CONNECTIONS:
        start = handLms.landmark[conn[0]]
        end = handLms.landmark[conn[1]]
        h, w, _ = frame.shape

        x1, y1 = int(start.x * w), int(start.y * h)
        x2, y2 = int(end.x * w), int(end.y * h)

        cv2.line(frame, (x1, y1), (x2, y2), color, 2)

    for lm in handLms.landmark:
        h, w, _ = frame.shape
        x, y = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (x, y), 5, color, -1)

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
                draw_colored_hand(frame, handLms, LEFT_COLOR)
            else:
                right_lm = lm
                right_pos = (x, y)
                draw_colored_hand(frame, handLms, RIGHT_COLOR)

    return frame, left_lm, right_lm, left_pos, right_pos