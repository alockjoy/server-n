from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import fitz  # PyMuPDF
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
    os.remove(pdf_path)  # ফাইল ব্যবহারের পর ডিলিট

    data = parse_nid_text(text)
    return JSONResponse(content=data)


def extract_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def parse_nid_text(text):
    # regex pattern গুলো বাংলা ও ইংরেজি দুটো ক্ষেত্রেই কাজ করবে এমনভাবে সাজানো

    def find(pattern, default=""):
        match = re.search(pattern, text, re.MULTILINE)
        return match.group(1).strip() if match else default

    return {
        "national_id": find(r"জাতীয়\s*পরিচয়পত্র\s*[:\-]?\s*(\d+)|National\s*ID\s*[:\-]?\s*(\d+)") or "",
        "pin": find(r"পিন\s*[:\-]?\s*(\d+)|Pin\s*[:\-]?\s*(\d+)") or "",
        "name_bangla": find(r"নাম\s*\(বাংলা\)\s*[:\-]?\s*(.+?)\n|Name\s*\(Bangla\)\s*[:\-]?\s*(.+?)\n") or "",
        "name_english": find(r"নাম\s*\(ইংরেজি\)\s*[:\-]?\s*([A-Za-z\s]+)|Name\s*\(English\)\s*[:\-]?\s*([A-Za-z\s]+)") or "",
        "date_of_birth": find(r"জন্মতারিখ\s*[:\-]?\s*([\d\-/]+)|Date\s*of\s*Birth\s*[:\-]?\s*([\d\-/]+)") or "",
        "father_name": find(r"পিতার\s*নাম\s*[:\-]?\s*(.+?)\n|Father\s*Name\s*[:\-]?\s*(.+?)\n") or "",
        "mother_name": find(r"মাতার\s*নাম\s*[:\-]?\s*(.+?)\n|Mother\s*Name\s*[:\-]?\s*(.+?)\n") or "",
        "spouse_name": find(r"স্বামীর\s*বা\s*স্ত্রীর\s*নাম\s*[:\-]?\s*(.+?)\n|Spouse\s*Name\s*[:\-]?\s*(.+?)\n") or "",
        "gender": find(r"লিঙ্গ\s*[:\-]?\s*(\w+)|Gender\s*[:\-]?\s*(\w+)") or "",
        "marital_status": find(r"বৈবাহিক\s*অবস্থা\s*[:\-]?\s*(\w+)|Marital\s*Status\s*[:\-]?\s*(\w+)") or "",
        "occupation": find(r"পেশা\s*[:\-]?\s*(.+?)\n|Occupation\s*[:\-]?\s*(.+?)\n") or "",
        "present_address": {
            "division": find(r"বর্তমান\s*ঠিকানা\s*বিভাগ\s*[:\-]?\s*(.+?)\n|Present\s*Address\s*Division\s*[:\-]?\s*(.+?)\n") or "",
            "district": find(r"জেলা\s*[:\-]?\s*(.+?)\n|District\s*[:\-]?\s*(.+?)\n") or "",
            "upozila": find(r"উপজেলা\s*[:\-]?\s*(.+?)\n|Upozila\s*[:\-]?\s*(.+?)\n") or "",
            "union": find(r"ইউনিয়ন/ওয়ার্ড\s*[:\-]?\s*(.+?)\n|Union/Ward\s*[:\-]?\s*(.+?)\n") or "",
            "post_office": find(r"ডাকঘর\s*[:\-]?\s*(.+?)\n|Post\s*Office\s*[:\-]?\s*(.+?)\n") or "",
            "postal_code": find(r"পোস্টাল\s*কোড\s*[:\-]?\s*(\d+)|Postal\s*Code\s*[:\-]?\s*(\d+)") or "",
        },
        "religion": find(r"ধর্ম\s*[:\-]?\s*(\w+)|Religion\s*[:\-]?\s*(\w+)") or "",
        "blood_group": find(r"রক্তের\s*গ্রুপ\s*[:\-]?\s*(\w+)|Blood\s*Group\s*[:\-]?\s*(\w+)") or "",
    }
