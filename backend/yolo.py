from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # placeholder until Ina's model is ready  # Ina's trained weights, place in backend/

def detect(image_path: str):
    results = model(image_path)[0]
    if len(results.boxes) == 0:
        return None
    box = results.boxes[0]
    species = results.names[int(box.cls)]
    confidence = float(box.conf)
    return species, confidence