import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

def process_hands(frame, w, h):
    rgb = frame[:, :, ::-1]
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

            if hand_label == "Right":
                left_lm = lm
                left_pos = (x, y)
            else:
                right_lm = lm
                right_pos = (x, y)

            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
    
    if left_pos and right_pos:
        if left_pos[0] > right_pos[0]:   # se foram trocadas
            left_lm, right_lm = right_lm, left_lm
            left_pos, right_pos = right_pos, left_pos

    return frame, left_lm, right_lm, left_pos, right_pos
