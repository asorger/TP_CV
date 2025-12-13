from ultralytics import YOLO

model = YOLO("yolov8n.pt")

BOOK_CLASS = [73]
CAN_CLASSES = [39, 41]


def detect_book(frame):
    results = model(frame, verbose=False, conf=0.25)
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])

            if cls not in BOOK_CLASS:
                continue

            x1, y1, x2, y2 = box.xyxy[0]
            w = x2 - x1
            h = y2 - y1

            if h / w < 1.1:
                continue

            if w < 60 or h < 90:
                continue

            return True
    return False


def detect_can(frame):
    results = model(frame, verbose=False, conf=0.25)
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])

            if cls not in CAN_CLASSES:
                continue

            x1, y1, x2, y2 = box.xyxy[0]
            w = x2 - x1
            h = y2 - y1

            if h / w < 1.3:
                continue

            if w < 30 or h < 60:
                continue

            return True

    return False
