import streamlit as st
from PIL import Image, ImageOps
import requests
import io, os, time, threading
from queue import Queue
from typing import Dict
import numpy as np
import base64
import cv2
from typing import Tuple, Dict

CROP_API = os.getenv("CROP_API", "http://localhost:/")

#Page config
st.set_page_config(
    page_title="Citizen ID OCR System",
    page_icon="🆔",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Multi-language text
LANGUAGES = {"vi": "Tiếng Việt", "en": "English"}
T = {
    "header_title": {
        "vi": "CITIZEN ID OCR SYSTEM",
        "en": "CITIZEN ID OCR SYSTEM"
    },
    "header_subtitle": {
        "vi": "Powered by NhutTran",
        "en": "Powered by NhutTran"
    },
    "header_note": {
        "vi": "Lưu ý: Đây chỉ là demo phục vụ quá trình nghiên cứu và học tập, hệ thống sẽ không thu thập bất cứ thông tin cá nhân nào từ bạn, đừng ngại trải nghiệm nhé !",
        "en": "Note: This is just a demo for research and learning purposes, the system will not collect any personal information from you, don't hesitate to experience it."
    },
    "upload_prompt": {
        "vi": "📤 Tải lên ảnh CCCD",
        "en": "📤 Upload your ID photo"
    },
    "upload_help": {
        "vi": "Chọn ảnh CCCD rõ nét, đủ sáng để có kết quả tốt nhất",
        "en": "Choose a clear, well-lit ID photo for best results"
    },
    "button_process": {
        "vi": "🔍 Trích xuất thông tin",
        "en": "🔍 Extract Information"
    },
    "status_success": {
        "vi": "✅ Trích xuất thành công",
        "en": "✅ Extraction successful"
    },
    "status_error": {
        "vi": "❌ Xử lý thất bại",
        "en": "❌ Processing error"
    },
    "api_spinner": {
        "vi": "🤖 Đang phân tích ảnh CCCD...",
        "en": "🤖 AI is analyzing your ID..."
    },
    "timeout_error": {
        "vi": "⏰ Timeout: API mất quá lâu.",
        "en": "⏰ Timeout: API took too long."
    },
    "no_file": {
        "vi": "❌ Vui lòng tải lên file!",
        "en": "❌ Please upload a file!"
    },
    "invalid_type": {
        "vi": "❌ Sai định dạng file.",
        "en": "❌ Invalid file type."
    },
    "too_large": {
        "vi": "❌ File quá lớn.",
        "en": "❌ File too large."
    }
}
def t(key: str) -> str:
    return T[key][lang_code]

#Language selector
lang = st.sidebar.selectbox(
    "🌐 Language / Ngôn ngữ",
    list(LANGUAGES.values()),
    index=0
)
lang_code = "en" if lang == LANGUAGES["en"] else "vi"

#CSS styling
st.markdown("""
<style>
  body { background: #f0f2f6; }
  .main-header { background: linear-gradient(135deg,#05999e,#cbe7e3);
                  padding: 0.75rem 1rem; border-radius: 8px;
                  color:#fff; text-align:center; margin-bottom:1rem;
                  box-shadow:0 4px 16px rgba(0,0,0,0.1);}
  .main-header h1 { margin:0.2rem 0; font-size:2rem; }
  .main-header p { margin:0.1rem 0; font-size:0.9rem; color:#f2f2f2; }
  .upload-label { font-size:1.2rem; font-weight:600; }
  .stButton>button { background:linear-gradient(135deg,#ff7e5f,#feb47b);
                      color:white; border:none; padding:0.75rem 2rem;
                      border-radius:6px; font-weight:600;
                      box-shadow:0 4px 12px rgba(0,0,0,0.1); }
  .stButton>button:hover { transform:translateY(-2px); }
  .result-card { background:white; border-radius:8px;
                 padding:1rem; margin-bottom:1rem;
                 box-shadow:0 2px 8px rgba(0,0,0,0.05); }
  .result-label { font-weight:600; color:#555; }
  .result-value { font-size:1.1rem; color:#222; }
  .loading-overlay { position:fixed; top:0; left:0; right:0; bottom:0;
                     background:rgba(255,255,255,0.8);
                     display:flex; align-items:center;
                     justify-content:center; z-index:999; }
</style>
""", unsafe_allow_html=True)


#Helper functions
def validate_image(uploaded) -> Tuple[bool, str]:
    if not uploaded:
        return False, t("no_file")
    ext = uploaded.name.lower().split('.')[-1]
    if ext not in ["jpg","jpeg","png"]:
        return False, t("invalid_type")
    if len(uploaded.getvalue()) > 50*1024*1024:
        return False, t("too_large")
    return True, ""


def detect_and_crop(pil_img: Image.Image) -> Image.Image:
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG")
    buf.seek(0)
    files = {"file": ("cccd.jpg", buf.read(), "image/jpeg")}
    resp = requests.post(CROP_API, files=files, timeout=30)
    resp.raise_for_status()
    b64 = resp.json()["crop_b64"]
    img_bytes = base64.b64decode(b64)
    return Image.open(io.BytesIO(img_bytes))

def preview_fixed(img: Image.Image, width: int=350, height: int=400):
    """Render a fixed-size preview box."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = base64.b64encode(buf.getvalue()).decode()
    html = f'''
    <div style="
      width:{width}px; height:{height}px;
      border:1px solid #ddd; overflow:hidden;
      display:flex; align-items:center; justify-content:center;
      background:#fafafa; margin-bottom:1rem;">
      <img src="data:image/png;base64,{data}"
           style="max-width:100%; max-height:100%;" />
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

def call_api(buf: io.BytesIO) -> Dict:
    buf.seek(0)
    files = {"file": ("cccd.jpg", buf.read(), "image/jpeg")}
    resp = requests.post(f"{os.getenv('API_URL','http://localhost:')}/",
                         files=files, timeout=60)
    resp.raise_for_status()
    return resp.json()

def display_results(res: Dict):
    fields = [
        ("full_name",    {"vi": "Họ và tên",        "en": "Full Name"}),
        ("id_number",    {"vi": "Số CCCD",          "en": "ID Number"}),
        ("date_of_birth",{"vi": "Ngày sinh",        "en": "Date of Birth"}),
        ("gender",       {"vi": "Giới tính",        "en": "Gender"}),
        ("expiry_date",  {"vi": "Ngày hết hạn",      "en": "Expiry Date"}),
        ("origin",       {"vi": "Quê quán",         "en": "Origin"}),
        ("residence",    {"vi": "Nơi thường trú",   "en": "Residence"}),
    ]

    # Badge
    st.markdown(
        f"<div class='result-card'><div class='result-label'>{t('status_success')}</div></div>",
        unsafe_allow_html=True
    )

    # Loop
    for key, labels in fields:
        label = labels[lang_code]
        value = res.get(key, "-")
        st.markdown(f"""
        <div class="result-card">
          <div class="result-label">{label}:</div>
          <div class="result-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🔍 Raw JSON"):
        st.json(res)        

#Build UI
# Header
st.markdown(f"""
<div class="main-header">
  <h1>{t('header_title')}</h1>
  <p>{t('header_subtitle')}</p>
</div>
<p style="text-align:center; margin-top:-0.5rem; font-style:italic; color:#555;">{t('header_note')}</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"<p class='upload-label'>{t('upload_prompt')}</p>", unsafe_allow_html=True)
    st.write(t('upload_help'))
    uploaded = st.file_uploader(
        label="Chọn file ảnh",
        type=['jpg','jpeg','png'],
        help=t("upload_help"),
        label_visibility="collapsed"
    )

    valid, msg = validate_image(uploaded)
    if not valid:
        st.error(msg)
    elif uploaded:
        # 1) EXIF orientation
        raw = Image.open(uploaded)
        img = ImageOps.exif_transpose(raw)
        # 2) Detect & crop
        cropped = detect_and_crop(img)
        # 3) Preview fixed
        preview_fixed(cropped)

with col2:
    if st.button(t("button_process")) and uploaded and valid:
        # loading overlay
        lid = st.empty()
        # serialize cropped
        buf = io.BytesIO()
        cropped.save(buf, format="JPEG")
        # worker thread
        q = Queue()
        def _worker(b, queue):
            try:
                data = call_api(b)
                queue.put(("ok", data))
            except Exception as e:
                queue.put(("error", str(e)))
        threading.Thread(target=_worker, args=(buf, q), daemon=True).start()
        pct = 0
        progress = st.progress(pct)

        while q.empty():
            time.sleep(0.2)
            pct = min(pct + 10, 90)
            progress.progress(pct)
        status, payload = q.get()
        progress.progress(100)
        lid.empty()
        if status=="ok":
            display_results(payload)
        else:
            st.error(f"{t('status_error')} {payload}")