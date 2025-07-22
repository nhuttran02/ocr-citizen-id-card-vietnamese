# Citizen ID OCR System (Vietnam CCCD)

> **Note:** This project is for **research and learning purposes only**.  
> The system **does not store, share, or use any personal data** beyond technical demonstration.

---

## Demo Video

[Video](https://drive.google.com/file/d/1-OtYeo2Q6xAp6h9X56H2Ky8Y9L9qVM76/view?usp=sharing)

---

## Goal

- Automatically extract key fields from Vietnamese Citizen ID (CCCD) images:  
  **Full Name, ID Number, Date of Birth, Gender, Expiry Date, Place of Origin, Permanent Residence**.
- Follow a classic OCR pipeline: **Detect → Crop → OCR** to balance accuracy and speed.

---

## Architecture Overview

### 3 Core Services (3 Docker Images)

| Service | Role | Short Description |
|---------|------|-------------------|
| **UI (Streamlit)** | User interface | Upload image, preview, loading effect, show results & raw JSON |
| **Crop Service (YOLO)** | Image pre-processing | Detect CCCD card region (YOLO) and crop out the background |
| **OCR API (YOLO + VietOCR)** | Text recognition | Detect text fields + VietOCR to read text, return JSON |

### Processing Flow (Mermaid)
    User->>UI: Upload CCCD image
    UI->>Crop: POST /crop (file)
    Crop-->>UI: Cropped image (Base64)
    UI->>OCR: POST /predict (cropped image)
    OCR-->>UI: JSON result
    UI-->>User: Display fields & Raw JSON
---
## Key Features
-  Smart crop of the CCCD area to reduce background noise.

-  Raw JSON viewer (toggleable).

-  Fixed-size preview so the layout doesn’t jump with different image sizes.

-  Bilingual UI (VI/EN) with runtime switching.

---
## Tech Stack
- CV & OCR: YOLO (detect), VietOCR, OpenCV, Pillow

- Backends: FastAPI + Uvicorn

- Frontend: Streamlit

- Containerization: Docker & Docker Compose
---

##  Project Structure
```
ocr-citizen-id-card-vietnamese/
├── ui/                      # Streamlit UI
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── detect-service/          # Crop service
│   ├── app.py
│   ├── models/card-detect-v2.pt
│   └── Dockerfile
├── ocr-api/                 # Detect & Extract service
│   ├── app/main.py
│   └── Dockerfile
└── README.md
```
---

📄 License
- For educational and research use only.
- Please contact the author for commercial usage.

---
👨‍💻 Author
NhutTran
Email: nhuttran230902@gmail.com