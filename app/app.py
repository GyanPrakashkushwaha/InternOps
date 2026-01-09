
from langchain_community.document_loaders import TextLoader
from PyPDF2 import PdfReader
from fastapi import FastAPI, UploadFile, File, Form
from base64 import b64encode
from typing import Literal
import io
from .database import init_db

# Celery
from .tasks import celery_app, analyze_task
from celery.result import AsyncResult

app = FastAPI()

@app.get("/")
def root():
    return {"message": "background is running!"}

@app.post("/analyze/{mode}")
async def analysis(
    mode: Literal["strict", "real-world", "brutal"],
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    contents = await file.read()
    pdf_file_object = io.BytesIO(contents)
    pdf_reader = PdfReader(pdf_file_object)
    
    text_content = ""
    for page in pdf_reader.pages:
        text_content += page.extract_text() or ""
    
    # Trigger Background Task 
    task = analyze_task.delay(resume_text = text_content, job_description = job_description, mode = mode)
    
    return {
        "message": "Analysis Started",
        "task_id": task.id,
        "mode": mode
    }
    
@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app = celery_app)
    
    if result.ready():
        if result.successful():
            return {
                "status": "completed",
                "data": result.get()
            }
        else:
            return {
                "status": "failed",
                "error": str(result.result)
            }
    else:
        return {"status": "processing"}
    
@app.on_event("startup")
def startup():
    print("======================================================== \n DATABASE CREATED\n ========================================================")
    init_db()