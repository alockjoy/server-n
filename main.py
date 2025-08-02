# main.py

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import os
import re

app = FastAPI()

@app.post("/upload-pdf/")
async def extract_info(pdf: UploadFile = File(...)):
    contents = await pdf.read()
    temp_path = f"temp/{pdf.filename}"
    os.makedirs("temp", exist_ok=True)

    with open(temp_path, "wb") as f:
        f.write(contents)

    doc = fitz.open(temp_path)
    text = ""
    for page in doc:
        text += page.get_text()

    os.remove(temp_path)

    def find(key):
        match = re.search(rf"{key}\\s+(.+)", text)
        return match.group(1).strip() if match else ""

    data = {
        "nid": find("National ID"),
        "pin": find("Pin"),
        "name_bangla": find("Name\\(Bangla\\)"),
        "name_english": find("Name\\(English\\)"),
        "date_of_birth": find("Date of Birth"),
        "birth_place": find("Birth Place"),
        "father_name": find("Father Name"),
        "mother_name": find("Mother Name"),
        "spouse_name": find("Spouse Name"),
        "gender": find("Gender"),
        "marital_status": find("Marital"),
        "occupation": find("Occupation"),
        "present_address": {
            "division": find("Present Address Division"),
            "district": find("District"),
            "upozila": find("Upozila"),
            "union": find("Union/Ward"),
            "village": find("Village/Road"),
            "post_office": find("Post Office"),
            "postal_code": find("Postal Code"),
        },
        "permanent_address": {
            "division": find("Permanent Address Division"),
            "district": find("District"),
            "upozila": find("Upozila"),
            "union": find("Union/Ward"),
            "village": find("Village/Road"),
            "post_office": find("Post Office"),
            "postal_code": find("Postal Code"),
        },
        "education": find("Education"),
        "religion": find("Religion")
    }

    return JSONResponse(content=data)
