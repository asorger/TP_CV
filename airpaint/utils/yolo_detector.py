from ultralytics import YOLO

# ============================
# Modelo YOLOv8 (Ultralytics)
# ============================
# Carrega um modelo pré-treinado (YOLOv8 nano) para deteção de objetos.
model = YOLO("yolov8n.pt")

# ============================
# Classes alvo (IDs COCO)
# ============================
# BOOK_CLASS: lista com o(s) ID(s) COCO considerados como "livro".
BOOK_CLASS = [73]

# CAN_CLASSES: lista com os ID(s) COCO considerados como "lata" (ex.: garrafa/recipiente).
CAN_CLASSES = [39, 41]


def detect_book(frame):
    """
    Deteta se existe um "livro" no frame usando YOLO.

    Estratégia:
    - Corre o modelo YOLO no frame com conf=0.25.
    - Percorre todas as bounding boxes detetadas.
    - Filtra apenas as boxes cuja classe esteja em BOOK_CLASS.
    - Aplica filtros geométricos para reduzir falsos positivos:
      - Razão altura/largura: exige que o objeto seja relativamente "alto" (h/w >= 1.1)
      - Tamanho mínimo em pixels: w >= 60 e h >= 90
    - Se encontrar uma box válida, devolve True.

    Retorno:
    - bool: True se detetar um livro que passe os filtros, False caso contrário.
    """
    # Executa deteção no frame
    results = model(frame, verbose=False, conf=0.25)

    # Percorre resultados (pode haver vários "r" dependendo da API/execução)
    for r in results:
        # Percorre todas as bounding boxes detetadas
        for box in r.boxes:
            # Classe prevista (convertida para int)
            cls = int(box.cls[0])

            # Ignora classes que não sejam "livro"
            if cls not in BOOK_CLASS:
                continue

            # Coordenadas da bounding box (x1, y1, x2, y2)
            x1, y1, x2, y2 = box.xyxy[0]

            # Largura e altura da box
            w = x2 - x1
            h = y2 - y1

            # Filtro por formato: livros devem ser relativamente mais altos do que largos
            if h / w < 1.1:
                continue

            # Filtro por tamanho mínimo (evita deteções muito pequenas/ruído)
            if w < 60 or h < 90:
                continue

            # Encontrou um livro "válido"
            return True

    # Não encontrou livro
    return False


def detect_can(frame):
    """
    Deteta se existe uma "lata" no frame usando YOLO.

    Estratégia:
    - Corre o modelo YOLO no frame com conf=0.25.
    - Percorre todas as bounding boxes detetadas.
    - Filtra apenas as boxes cuja classe esteja em CAN_CLASSES.
    - Aplica filtros geométricos para reduzir falsos positivos:
      - Razão altura/largura: exige um objeto mais estreito e alto (h/w >= 1.3)
      - Tamanho mínimo em pixels: w >= 30 e h >= 60
    - Se encontrar uma box válida, devolve True.

    Retorno:
    - bool: True se detetar uma lata que passe os filtros, False caso contrário.
    """
    # Executa deteção no frame
    results = model(frame, verbose=False, conf=0.25)

    # Percorre resultados
    for r in results:
        # Percorre todas as bounding boxes detetadas
        for box in r.boxes:
            # Classe prevista
            cls = int(box.cls[0])

            # Ignora classes que não sejam as pretendidas
            if cls not in CAN_CLASSES:
                continue

            # Coordenadas da bounding box
            x1, y1, x2, y2 = box.xyxy[0]

            # Largura e altura da box
            w = x2 - x1
            h = y2 - y1

            # Filtro por formato: latas tendem a ser mais altas e estreitas
            if h / w < 1.3:
                continue

            # Filtro por tamanho mínimo
            if w < 30 or h < 60:
                continue

            # Encontrou uma lata "válida"
            return True

    # Não encontrou lata
    return False