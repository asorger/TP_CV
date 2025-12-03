from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_phone(frame):
    results = model(frame, verbose=False)
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls == 67:  # cell phone
                return True
    return False