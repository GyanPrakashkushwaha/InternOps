
from langchain_community.document_loaders import TextLoader
from fastapi import FastAPI, UploadFile, File, Form
from base64 import b64encode
from typing import Literal
from .utils import read_pdf, generate_hash
from .database import init_db, get_db_connection

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
    # fake_hash_key = "gyanprakash12"
    # hash_key = fake_hash_key
    
    # check if the hash key matches. 
    query = """
    SELECT id FROM analysis
    WHERE hash_key = %s 
    """
    cur.execute(query, (hash_key, ))
    analysis_id = cur.fetchone()
    
    if analysis_id:
        query = """
        SELECT * FROM ats
        WHERE analysis_id = %s;
        """
        cur.execute(query, (analysis_id[0],))
        ats_result_tuple = cur.fetchone()
        query = """
        SELECT * FROM recruiter
        WHERE analysis_id = %s;
        """        
        cur.execute(query, (analysis_id[0],))
        recruiter_result_tuple = cur.fetchone()
        query = """
        SELECT * FROM hiring_manager
        WHERE analysis_id = %s;
        """        
        cur.execute(query, (analysis_id[0],))
        hm_result_tuple = cur.fetchone()
        # format result
        ats_result = {
            "match_score": ats_result_tuple[2],
            "missing_keywords": ats_result_tuple[3],
            "formatting_issues": ats_result_tuple[4],
            "decision": ats_result_tuple[5],
            "feedback": ats_result_tuple[6],
        }

        recruiter_result = {
            "career_progression_score": recruiter_result_tuple[2],
            "red_flags": recruiter_result_tuple[3],
            "soft_skills_detected": recruiter_result_tuple[4],
            "decision": recruiter_result_tuple[5],
            "feedback": recruiter_result_tuple[6],
        }

        hm_result = {
            "tech_depth_score": hm_result_tuple[2],
            "project_impact_score": hm_result_tuple[3],
            "stack_alignment": hm_result_tuple[4],
            "decision": hm_result_tuple[5],
            "feedback": hm_result_tuple[6],
        }
        final_result = {
            "ats_result": ats_result,
            "recruiter_result": recruiter_result,
            "hm_result": hm_result
        }
        
        return {
            "status": "Completed",
            "final_result": final_result
        }
    
    # print(hash_key, job_description, resume_content, mode)
    # print(type(hash_key), type(job_description), type(resume_content), type(mode))
    analysis_id
    try:
        # id_query = 
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
    print("======================================================== \n DATABASE CREATED\n ========================================================")
    init_db()