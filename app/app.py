
import json
import asyncio
from contextlib import asynccontextmanager
from typing import Literal, AsyncGenerator

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from base64 import b64encode
from celery.result import AsyncResult

# Internal Modules
from .utils import read_pdf, generate_hash
from .database import init_db, get_db_connection, get_final_result, get_db_uri
from .tasks import celery_app, analyze_task


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "Backend is running!"}


@app.post("/analyze/{mode}")
async def analysis(
    mode: Literal["strict", "real-world", "brutal"],
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_content = await read_pdf(file)
    conn, cur = get_db_connection()
    
    try:
        resume_hash = generate_hash(resume_content)
        jd_hash = generate_hash(job_description)
        hash_key = f"{resume_hash}_{jd_hash}_{mode}"
        
        # Check cache
        cur.execute("SELECT id FROM analysis WHERE hash_key = %s", (hash_key, ))
        existing_id = cur.fetchone()
        
        if existing_id:
            # print("=========================================================================================")
            # print(existing_id)
            # print("=========================================================================================")
            final_result = get_final_result(existing_id["id"])
            print(final_result)
            print({"status": "Completed", "final_result": final_result, "analysis_id" : existing_id["id"]})
            return {"status": "Completed", "final_result": final_result, "analysis_id" : existing_id["id"]}
        
        # Create new entry
        query = """
        INSERT INTO analysis (hash_key, job_description, resume_text, mode)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        cur.execute(query, (hash_key, job_description, resume_content, mode))
        print("======================================== ANALYSIS ID =======================================")
        analysis_id = cur.fetchone()["id"]
        print(analysis_id)
        print("======================================== ANALYSIS ID =======================================")
        conn.commit()
        
        # Dispatch Celery Task
        task = analyze_task.delay(
            resume_text=resume_content, 
            job_description=job_description, 
            mode=mode, 
            hash_key=hash_key,
            analysis_id = analysis_id
        )
        
        return {
            "status": "Analysis Started",
            "task_id": task.id,
            "mode": mode,
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
        
        
@app.get("/analysis_result/{analysis_id}")
def get_analysis_result(analysis_id):
    final_result = get_final_result(analysis_id)
    # print(final_result)
    return {
            "status": "Completed",
            "final_result": final_result
        }

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        if result.successful():
            return {"status": "Completed", "final_result": result.get()}
        else:
            return {"status": "Failed", "error": str(result.result)}
    else:
        return {"status": "Processing"}
    

@app.get("/analysis_id_list")
def analysis_history():
    try:
        conn, cur = get_db_connection()
        query = """
        SELECT id FROM analysis
        """
        cur.execute(query)
        analysis_id = cur.fetchall()
        # print(analysis_id)
        return {
            "status": "done",
            "id_list": analysis_id
        }
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()

@app.get("/web/dashboard/history")
def fetch_dashboard_history():
    try:
        conn, cur = get_db_connection()

        query = """
            SELECT 
                a.id as id,
                a.created_at as date,
                SUBSTRING(a.job_description, 10, 35) as jdSnippet,
                a.mode as strategy, 
                ats.match_score as atsScore, 
                r.career_progression_score as recruiterScore, 
                hm.tech_depth_score as careerProgressionScore, 
                hm.project_impact_score as techDepthScore,
                hm.decision as status
                
            FROM analysis a
            JOIN ats
            ON ats.analysis_id = a.id
            JOIN recruiter r
            ON r.analysis_id = a.id
            JOIN hiring_manager hm
            ON hm.analysis_id = a.id
            
            ORDER BY date DESC
        """
        print("hi mdaljlsasdksd")
        cur.execute(query)
        rows = cur.fetchall()
        # print(rows)
        return {
            "status": "success",
            "data": {
                "history": rows
            }
        }

    except Exception as error:
        raise error

    finally:
        cur.close()
        conn.close()

@app.on_event("startup")
def startup():
    init_db()