import cv2
import os
import time
import numpy as np


class ToolWindow:
    """
    Janela auxiliar para mostrar uma animação (sprites/frames) da ferramenta atual
    (ex.: brush, eraser, spray) numa janela OpenCV separada.

    Ideia geral:
    - Carrega frames PNG (com ou sem alpha) de pastas dentro de um diretório base.
    - Mantém um índice por ferramenta e avança esse índice com um delay fixo.
    - Devolve sempre uma imagem (canvas) 300x300 pronta para ser mostrada no cv2.imshow().
    """

    def __init__(self, base_path=None):
        """
        Inicializa o ToolWindow.

        Parâmetros:
        - base_path: caminho opcional para a pasta base dos assets.
          Se None, usa por defeito ../assets relativo ao ficheiro atual.
        """
        # Diretório onde este ficheiro .py está localizado
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Define a pasta base de assets:
        # - por defeito: ../assets
        # - se base_path for fornecido: usa o caminho indicado
        if base_path is None:
            self.base_path = os.path.abspath(os.path.join(base_dir, "..", "assets"))
        else:
            self.base_path = os.path.abspath(base_path)

        # animations: dicionário { "tool": [frames...] }
        self.animations = {}

        # index: índice atual do frame para cada ferramenta
        self.index = {}

        # last_time: último instante em que o frame mudou, por ferramenta
        self.last_time = {}

        # Delay entre frames (segundos) para controlar a velocidade da animação
        self.delay = 0.08

        # Dimensões da janela/canvas retornado por get_frame()
        self.window_w = 300
        self.window_h = 300

        # Carrega todas as animações disponíveis
        self._load()

    def _load_frames(self, folder):
        """
        Carrega todos os frames (imagens) de uma pasta.

        - Ordena os nomes dos ficheiros para manter a sequência correta.
        - Lê com IMREAD_UNCHANGED para preservar canal alpha se existir (PNG com transparência).
        - Devolve uma lista de imagens (arrays NumPy).
        """
        frames = []

        # Se a pasta não existir, informa e devolve lista vazia
        if not os.path.exists(folder):
            print(f"[ToolWindow] Pasta não encontrada: {folder}")
            return frames

        # Percorre ficheiros ordenados (importante para animações frame_001, frame_002, etc.)
        for f in sorted(os.listdir(folder)):
            path = os.path.join(folder, f)

            # Lê mantendo alpha se houver (4 canais)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                frames.append(img)

        # Debug: mostra quantos frames foram carregados
        print(f"[ToolWindow] {folder}: {len(frames)} frames")
        return frames

    def _load(self):
        """
        Carrega as animações para cada ferramenta.

        Mapeamento:
        - "brush"  -> pasta "pencil"
        - "eraser" -> pasta "rubber"
        - "spray"  -> pasta "can"

        Também inicializa:
        - index[tool] = 0
        - last_time[tool] = time.time()
        """
        self.animations["brush"] = self._load_frames(os.path.join(self.base_path, "pencil"))
        self.animations["eraser"] = self._load_frames(os.path.join(self.base_path, "rubber"))
        self.animations["spray"] = self._load_frames(os.path.join(self.base_path, "can"))

        # Inicializa controlo de animação por ferramenta
        for k in self.animations:
            self.index[k] = 0
            self.last_time[k] = time.time()

    def get_frame(self, tool):
        """
        Devolve a imagem (canvas) 300x300 com a animação da ferramenta pedida.

        Passos:
        - Cria um canvas preto (BGR) do tamanho da janela.
        - Se a ferramenta não existir ou não tiver frames, escreve "NO TOOL" e devolve.
        - Caso exista:
          - atualiza o índice do frame baseado no delay
          - redimensiona o frame para caber na janela com margem (0.85)
          - centra o frame no canvas
          - se tiver alpha (4º canal), faz blending manual (overlay com transparência)
          - devolve o canvas final
        """
        # Canvas base (preto) onde a animação será desenhada
        canvas = np.zeros((self.window_h, self.window_w, 3), dtype=np.uint8)

        # Se a ferramenta não existir no dicionário ou não tiver frames carregados
        if tool not in self.animations or not self.animations[tool]:
            cv2.putText(
                canvas,
                "NO TOOL",
                (60, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )
            return canvas

        # Atualiza frame atual conforme o tempo (controlo de FPS da animação)
        now = time.time()
        if now - self.last_time[tool] >= self.delay:
            self.index[tool] = (self.index[tool] + 1) % len(self.animations[tool])
            self.last_time[tool] = now

        # Frame atual da animação
        frame = self.animations[tool][self.index[tool]]

        # Calcula escala para caber na janela (com margem 0.85 para não encostar às bordas)
        h, w = frame.shape[:2]
        scale = min(self.window_w / w, self.window_h / h) * 0.85
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)))

        # Coordenadas para centrar o frame no canvas
        y = (self.window_h - frame.shape[0]) // 2
        x = (self.window_w - frame.shape[1]) // 2

        # Se a imagem tiver 4 canais (BGRA), faz blending usando o canal alpha
        if frame.shape[2] == 4:
            alpha = frame[:, :, 3] / 255.0
            for c in range(3):
                canvas[y:y+frame.shape[0], x:x+frame.shape[1], c] = (
                    canvas[y:y+frame.shape[0], x:x+frame.shape[1], c] * (1 - alpha)
                    + frame[:, :, c] * alpha
                )
        else:
            # Se não houver alpha, copia diretamente para o canvas
            canvas[y:y+frame.shape[0], x:x+frame.shape[1]] = frame

        return canvas