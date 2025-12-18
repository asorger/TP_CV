import mediapipe as mp
import cv2

# mp_face aponta para o módulo Face Mesh do MediaPipe, usado para detetar landmarks faciais.
mp_face = mp.solutions.face_mesh

# Instância do FaceMesh configurada para:
# - detetar no máximo 1 face
# - refine_landmarks=True para landmarks mais detalhados (ex.: olhos/íris)
# - thresholds de confiança para deteção e tracking relativamente altos (0.7)
face = mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
 
# ============================
# Variáveis de controlo do estado de sorriso
# ============================
# Contador de frames consecutivos a sorrir
smile_counter = 0

# Contador de frames consecutivos sem sorriso (ou sem face detetada)
no_smile_counter = 0

# Número de frames consecutivos necessário para considerar "sorriso confirmado"
# (ajuda a reduzir falsos positivos por ruído)
SMILE_FRAMES = 5
 
def detect_smile(frame):
    """
    Deteta se existe um sorriso sustentado na imagem (frame) usando landmarks do FaceMesh.

    Estratégia:
    - Converte o frame para RGB (MediaPipe espera RGB).
    - Processa a face e obtém landmarks.
    - Mede a diferença vertical (em coordenadas normalizadas) entre o lábio superior e
      os cantos da boca (esquerdo e direito).
    - Se essa diferença ultrapassar um limiar em ambos os lados, assume que está a sorrir.
    - Usa contadores de frames para só confirmar sorriso após SMILE_FRAMES consecutivos.

    Retorno:
    - smile_state (bool): True quando o sorriso é considerado estável (>= SMILE_FRAMES)
    - landmarks_face (FaceLandmarks ou None): o objeto de landmarks da face, se existir
    """
    global smile_counter, no_smile_counter

    # Dimensões do frame (altura, largura, canais)
    h, w, _ = frame.shape

    # Conversão BGR -> RGB (OpenCV captura normalmente em BGR)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processamento do frame para deteção de face/landmarks
    results = face.process(rgb)
 
    # Se não houver face detetada:
    # - aumenta o contador de "sem sorriso"
    # - reseta o contador de sorriso
    # - devolve False e None (sem landmarks)
    if not results.multi_face_landmarks:
        no_smile_counter += 1
        smile_counter = 0
        return False, None
 
    # Extrai a lista de landmarks da primeira (e única) face
    lm = results.multi_face_landmarks[0].landmark
 
    # Landmarks específicos usados para estimar sorriso:
    # - 61: canto esquerdo da boca
    # - 291: canto direito da boca
    # - 13: região do lábio superior (ponto central superior)
    left_mouth = lm[61]
    right_mouth = lm[291]
    upper_lip = lm[13]
 
    # Calcula a "altura" relativa entre o lábio superior e cada canto da boca.
    # (coordenadas normalizadas: y aumenta de cima para baixo no ecrã)
    left_height = upper_lip.y - left_mouth.y
    right_height = upper_lip.y - right_mouth.y
 
    # Condição de "sorriso instantâneo" neste frame:
    # Se ambos os lados excederem um limiar, considera que está a sorrir agora.
    smiling_now = left_height > 0.008 and right_height > 0.008
 
    # Atualiza contadores para exigir consistência ao longo de frames consecutivos.
    if smiling_now:
        smile_counter += 1
        no_smile_counter = 0
    else:
        no_smile_counter += 1
        smile_counter = 0
 
    # Estado final: só True quando o sorriso foi detetado durante SMILE_FRAMES frames seguidos.
    smile_state = smile_counter >= SMILE_FRAMES
 
    # Devolve o estado do sorriso e os landmarks da face (para debug/visualização posterior).
    return smile_state, results.multi_face_landmarks[0]