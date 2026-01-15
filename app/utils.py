
from PyPDF2 import PdfReader
import io
import hashlib
import shutil
from pathlib import Path
import os

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok = True)

async def read_pdf(resume_pdf):
    contents = await resume_pdf.read()
    pdf_file_object = io.BytesIO(contents)
    pdf_reader = PdfReader(pdf_file_object)
    
    resume_content = ""
    for page in pdf_reader.pages:
        resume_content += page.extract_text() or ""

    return resume_content

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def save_pdf(pdf_file):
    file_path = os.path.join(UPLOAD_DIR, pdf_file.filename)
    if not os.path.exists(file_path):
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)
        
    