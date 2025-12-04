import mediapipe as mp
import cv2

mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

smile_counter = 0
no_smile_counter = 0
SMILE_FRAMES = 5


def detect_smile(frame):
    global smile_counter, no_smile_counter
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face.process(rgb)

    if not results.multi_face_landmarks:
        no_smile_counter += 1
        smile_counter = 0
        return False

    lm = results.multi_face_landmarks[0].landmark

    left_mouth = lm[61]
    right_mouth = lm[291]
    upper_lip = lm[13]

    left_height = upper_lip.y - left_mouth.y
    right_height = upper_lip.y - right_mouth.y

    smiling_now = left_height > 0.008 and right_height > 0.008

    if smiling_now:
        smile_counter += 1
        no_smile_counter = 0
    else:
        no_smile_counter += 1
        smile_counter = 0

    if smile_counter >= SMILE_FRAMES:
        return True

    if no_smile_counter >= SMILE_FRAMES:
        return False

    return smile_counter > no_smile_counter