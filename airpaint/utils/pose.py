import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)

def detect_pose(frame):
    h, w, _ = frame.shape
    rgb = frame[:, :, ::-1]
    results = pose.process(rgb)

    if not results.pose_landmarks:
        return False, False

    landmarks = results.pose_landmarks.landmark

    rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y

    lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y

    right_up = rw < rs - 0.05
    left_up  = lw < ls - 0.05

    return right_up, left_up