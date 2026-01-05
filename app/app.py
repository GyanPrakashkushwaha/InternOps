
from langchain_community.document_loaders import TextLoader
from PyPDF2 import PdfReader
from fastapi import FastAPI, UploadFile, File, Form
from base64 import b64encode
import io

# Local Module Import
from .main import workflow

app = FastAPI()

@app.get("/")
def root():
    return {"message": "background is running!"}

@app.post("/analyze")
async def analysis(
    file: UploadFile = File(...),
    jobDescription: str = Form(...)
):
    contents = await file.read()
    pdf_file_object = io.BytesIO(contents)

    pdf_reader = PdfReader(pdf_file_object)
    text_content = ""

    for page in pdf_reader.pages:
        text_content += page.extract_text() or ""
    
    input_state = {
        "resume_text": text_content,
        "job_description": jobDescription
    }
    
    output_state = workflow.invoke(input_state)
    

    return {
        "result": output_state
    }

# final_state = workflow.invoke(initial_state)
# print(final_state)
