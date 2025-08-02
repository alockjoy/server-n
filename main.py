from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import os
import re

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/extract-nid/")
async def extract_nid_info(pdf: UploadFile = File(...)):
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)

    with open(pdf_path, "wb") as f:
        f.write(await pdf.read())

    text = extract_text(pdf_path)
    os.remove(pdf_path)

    data = parse_nid_text(text)
    return JSONResponse(content=data)


def extract_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def parse_nid_text(text):
    def find(pattern, default=""):
        match = re.search(pattern, text, re.MULTILINE)
        return match.group(1).strip() if match else default

    return {
        "photo": "https://example.com/photo.jpg",  # Placeholder
        "sign": "https://example.com/sign.jpg",    # Placeholder
        "nameBen": find(r"নাম\s*[:\-]?\s*(.+)", ""),  # Bangla name
        "nameEng": find(r"Name\(English\)\s*[:\-]?\s*([A-Z\s]+)", ""),
        "national_id": find(r"National ID\s*[:\-]?\s*(\d+)", ""),
        "pin": find(r"Pin\s*[:\-]?\s*(\d+)", ""),
        "father": find(r"Father Name\s*[:\-]?\s*(.+)", ""),
        "mother": find(r"Mother Name\s*[:\-]?\s*(.+)", ""),
        "birth_place": find(r"Place of Birth\s*[:\-]?\s*(.+)", ""),
        "birth": find(r"Date of Birth\s*[:\-]?\s*([\d\-]+)", ""),
        "blood": find(r"Blood Group\s*[:\-]?\s*(\w+)", ""),
        "address": find(r"Present Address\s*[:\-]?\s*(.+)", "")
    }
