import os
from ultralytics import YOLO
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import cv2
from PIL import Image

def load_models(model_dir: str, device: str = "cpu"):
    paths = {
        'ocr1': os.path.join(model_dir, ''),
        'ocr2': os.path.join(model_dir, ''),
        'ocr3': os.path.join(model_dir, '')
    }
    # Load YOLO models (device sẽ được chỉ định lúc inference)
    models = { key: YOLO(path) for key, path in paths.items() }

    # Load VietOCR
    cfg = Cfg.load_config_from_name('vgg_transformer')
    cfg['device'] = device
    vietocr = Predictor(cfg)

    return models, vietocr


def detect_and_ocr(model: YOLO, ocr: Predictor, image_path: str, device: str = "cpu") -> dict:
    results = model(image_path, device=device)
    boxes = results[0].boxes.xyxy.cpu().numpy()
    labels = results[0].boxes.cls.cpu().numpy().astype(int)
    names = results[0].names

    img = cv2.imread(image_path)
    output = {}
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = [int(v) for v in box]
        crop = img[y1:y2, x1:x2]
        crop_pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        text = ocr.predict(crop_pil)
        label = names[labels[i]]
        output[label] = text
    return output


def merge_ocr3(parts: dict, key1: str, key2: str) -> str:
    v1 = parts.get(key1, '')
    v2 = parts.get(key2, '')
    if v1 and v2:
        return f"{v1} {v2}"
    return v1 or v2 or ''


def process_image(image_path: str, models: dict, ocr: Predictor, device: str = "cpu") -> dict:
    out_name = detect_and_ocr(models['ocr1'], ocr, image_path, device)
    out_dob  = detect_and_ocr(models['ocr2'], ocr, image_path, device)
    out_addr = detect_and_ocr(models['ocr3'], ocr, image_path, device)

    data = {**out_name, **out_dob, **out_addr}
    data['origin']    = merge_ocr3(data, 'ori_1', 'ori_2')
    data['residence'] = merge_ocr3(data, 'res_1', 'res_2')

    return {
        'full_name':     data.get('name', ''),
        'id_number':     data.get('num_id', ''),
        'date_of_birth': data.get('dob', ''),
        'gender':        data.get('gender', ''),
        'expiry_date':   data.get('ex', ''),
        'origin':        data.get('origin', ''),
        'residence':     data.get('residence', '')
    }