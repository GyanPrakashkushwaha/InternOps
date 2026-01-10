

from PyPDF2 import PdfReader
import io
import hashlib

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
