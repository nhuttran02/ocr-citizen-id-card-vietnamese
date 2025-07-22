from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import numpy as np
import cv2
import base64

# Load model
model = YOLO("models/")

app = FastAPI(title="CCCD Crop Service by nhuttran")

@app.post("/")
async def crop_card(file: UploadFile = File(...), pad: int = 20):
    # Read upload bytes and decode to BGR image
    data = await file.read()
    img_array = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Perform detection
    res = model.predict(img, conf=0.25, verbose=False)[0]
    boxes = res.boxes.xyxy.cpu().numpy()

    # Determine cropped region
    if boxes.size == 0:
        cropped = img
    else:
        areas = (boxes[:,2] - boxes[:,0]) * (boxes[:,3] - boxes[:,1])
        x1, y1, x2, y2 = boxes[np.argmax(areas)].astype(int)
        h, w = img.shape[:2]
        x1, y1 = max(x1 - pad, 0), max(y1 - pad, 0)
        x2, y2 = min(x2 + pad, w), min(y2 + pad, h)
        cropped = img[y1:y2, x1:x2]

    # Encode cropped image as JPEG then Base64
    success, buffer = cv2.imencode('.jpg', cropped)
    if not success:
        return {"error": "Failed to encode image"}
    b64 = base64.b64encode(buffer).decode('ascii')
    return {"crop_b64": b64}