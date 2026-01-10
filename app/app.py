
from langchain_community.document_loaders import TextLoader
from fastapi import FastAPI, UploadFile, File, Form
from base64 import b64encode
from typing import Literal
from .utils import read_pdf, generate_hash
from .database import init_db, get_db_connection, get_final_result

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
    resume_content = await read_pdf(file)
    conn, cur = get_db_connection()
    resume_hash = generate_hash(resume_content)
    jd_hash = generate_hash(job_description)
    hash_key = f"{resume_hash}_{jd_hash}_{mode}"
    
    # check if the hash key matches.
    query = """
    SELECT id FROM analysis
    WHERE hash_key = %s
    """
    cur.execute(query, (hash_key, ))
    analysis_id = cur.fetchone()
    
    if analysis_id:
        final_result = get_final_result(analysis_id)
        
        return {
            "status": "Completed",
            "final_result": final_result
        }
    
    try:
        query = """
        INSERT INTO analysis (hash_key, job_description, resume_text, mode)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        cur.execute(query, (hash_key, job_description, resume_content, mode))
        analysis_id = cur.fetchone()[0]
        # print(analysis_id)
        conn.commit()
        # 10/0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
        
    task = analyze_task.delay(
        resume_text = resume_content, 
        job_description = job_description, 
        mode = mode, 
        hash_key = hash_key,
        analysis_id = analysis_id
        )
    
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
    init_db()