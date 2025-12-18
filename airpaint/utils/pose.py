import mediapipe as mp

# ============================
# Configuração do MediaPipe Pose
# ============================
# Referência ao módulo Pose do MediaPipe (deteção de corpo inteiro / esqueleto).
mp_pose = mp.solutions.pose

# Instância do detector de pose:
# - min_detection_confidence=0.6: confiança mínima para a deteção inicial
# - min_tracking_confidence=0.6: confiança mínima para tracking entre frames
pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)


def detect_pose(frame):
    """
    Deteta pose (landmarks do corpo) e determina se os braços estão levantados.

    Estratégia:
    - Converte o frame para RGB (aqui usando slicing frame[:, :, ::-1] que inverte BGR->RGB).
    - Processa com MediaPipe Pose para obter landmarks.
    - Se não houver landmarks, devolve False, False, None.
    - Caso haja landmarks:
      - Compara a altura (coordenada y) do pulso com a do ombro.
      - Se o pulso estiver significativamente acima do ombro (y menor),
        considera o braço "levantado".

    Retorno:
    - right_up (bool): True se o pulso direito estiver acima do ombro direito (com margem)
    - left_up (bool): True se o pulso esquerdo estiver acima do ombro esquerdo (com margem)
    - pose_landmarks (objeto MediaPipe ou None): landmarks completos para debug/desenho
    """
    # Dimensões do frame (altura, largura, canais)
    h, w, _ = frame.shape

    # Conversão BGR -> RGB (forma rápida: inverte o último eixo dos canais)
    rgb = frame[:, :, ::-1]

    # Processa o frame para detetar pose
    results = pose.process(rgb)

    # Se não houver pose detetada, devolve estado negativo e sem landmarks
    if not results.pose_landmarks:
        return False, False, None

    # Lista de landmarks (pontos do corpo) com coordenadas normalizadas (0..1)
    landmarks = results.pose_landmarks.landmark

    # Coordenadas y do pulso e ombro direitos
    rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y

    # Coordenadas y do pulso e ombro esquerdos
    lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y

    # Braço "levantado" se o pulso estiver pelo menos 0.05 acima do ombro
    # (lembrar: em imagem, y menor = mais acima)
    right_up = rw < rs - 0.05
    left_up = lw < ls - 0.05

    # Devolve os estados e os landmarks completos da pose
    return right_up, left_up, results.pose_landmarks