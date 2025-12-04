import mediapipe as mp
import cv2
import math

mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

def euclidean(a, b):
    return math.dist([a.x, a.y], [b.x, b.y])

def detect_smile(frame):
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face.process(rgb)

    if not results.multi_face_landmarks:
        return False

    lm = results.multi_face_landmarks[0].landmark

    left_mouth = lm[61]
    right_mouth = lm[291]
    upper_lip = lm[13]
    lower_lip = lm[14]

    mouth_width = euclidean(left_mouth, right_mouth)
    mouth_height = euclidean(upper_lip, lower_lip)

    if mouth_height == 0:
        return False

    ratio = mouth_width / mouth_height

    return ratio > 2.0