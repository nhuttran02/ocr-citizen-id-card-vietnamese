import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict
from app.ocr_service import load_models, process_image

app = FastAPI(title="OCR CCCD Service")

MODEL_DIR = os.getenv('MODEL_DIR', 'models')
DEVICE    = os.getenv('DEVICE', 'cpu')
models, vietocr = load_models(MODEL_DIR, DEVICE)

@app.post('/')
async def predict(file: UploadFile = File(...)) -> Dict:
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Invalid image format")

    temp_path = os.path.join('/tmp', file.filename)
    with open(temp_path, 'wb') as f:
        f.write(await file.read())

    try:
        result = process_image(temp_path, models, vietocr, DEVICE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_path)

    return JSONResponse(content=result)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    uvicorn.run('app.main:app', host='0.0.0.0', port=port, reload=True)