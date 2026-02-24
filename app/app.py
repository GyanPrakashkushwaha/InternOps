from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from .auth import get_password_hash, verify_password, create_access_token, get_current_user_id, get_optional_user_id
from .models import UserCreate, Token
from .database_queries import GET_USER_BY_EMAIL_QUERY, INSERT_USER_QUERY

import json
import asyncio
from typing import Literal

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Internal Modules
from .utils import read_pdf, generate_hash
from .database import init_db, get_db_connection, get_final_result
from .analyze import analyze_task
from .database_queries import (
    DASHBOARD_HISTORY_QUERY,
    ANALYSIS_TABLE_INSERTION_QUERY,
    ANALYSIS_HISTORY_QUERY
)

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
    return {"message": "InternOps Backend is running!"}

@app.on_event("startup")
def startup():
    init_db()

@app.post("/analyze/{mode}")
async def analysis(
    mode: Literal["strict", "real-world", "brutal"],
    file: UploadFile = File(...),
    job_description: str = Form(...),
    user_id: int = Depends(get_optional_user_id)
):
    resume_content = await read_pdf(file)
    conn, cur = get_db_connection()
    
    try:
        resume_hash = generate_hash(resume_content)
        jd_hash = generate_hash(job_description)
        hash_key = f"{resume_hash}_{jd_hash}_{mode}"
        
        # Check cache / existing analysis
        cur.execute("SELECT id FROM analysis WHERE hash_key = %s", (hash_key, ))
        existing_id = cur.fetchone()
        
        if existing_id:
            final_result = get_final_result(existing_id["id"])
            return {
                "status": "Completed", 
                "final_result": final_result,
                "analysis_id": existing_id["id"],
                "cached": True
            }
        
        # Create new entry in DB (Status Pending)
        cur.execute(ANALYSIS_TABLE_INSERTION_QUERY, (hash_key, job_description, resume_content, mode, user_id))
        row = cur.fetchone()
        analysis_id = row["id"]
        conn.commit()
        
        # EXECUTE ANALYSIS DIRECTLY (Blocking/Sync-in-Async)
        # This replaces the Celery task.
        # Note: If this takes >60s (Vercel Pro) or >10s (Hobby), it may timeout.
        result_data = await analyze_task(
            resume_text=resume_content, 
            job_description=job_description, 
            mode=mode, 
            hash_key=hash_key,
            analysis_id=analysis_id
        )
        
        # Re-fetch formatted result to match the structure expected by frontend
        final_result = get_final_result(analysis_id)
        
        return {
            "status": "Completed",
            "final_result": final_result,
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
        
# @app.get("/analysis_result/{analysis_id}")
# def get_analysis_result(analysis_id):
#     final_result = get_final_result(analysis_id)
#     return {
#             "status": "Completed",
#             "final_result": final_result
#         }

@app.get("/analysis_id_list")
def analysis_history():
    try:
        conn, cur = get_db_connection()
        query = "SELECT id FROM analysis"
        cur.execute(query)
        analysis_id = cur.fetchall()
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
def fetch_dashboard_history(user_id: int = Depends(get_current_user_id)):
    try:
        conn, cur = get_db_connection()
        cur.execute(DASHBOARD_HISTORY_QUERY, (user_id,))
        rows = cur.fetchall()
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


@app.get("/web/analysis/history")
def fetch_analysis_history(user_id: int = Depends(get_current_user_id)):
    try:
        conn, cur = get_db_connection()
        cur.execute(ANALYSIS_HISTORY_QUERY, (user_id,))
        rows = cur.fetchall()
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
        
@app.get("/web/analysis/report/{id}")
def fetch_analysis_report(id):
    try:
        conn, cur = get_db_connection()
        
        if id == "latest":  # /latest
            cur.execute("""SELECT id FROM analysis
                            LIMIT 1;""")
            id = cur.fetchone()
        
        cur.execute("SELECT company_name, employment_type FROM job_metadata WHERE analysis_id = %s", (id,))
        role = cur.fetchone()
        
        cur.execute("SELECT mode FROM analysis WHERE id = %s", (id,))
        mode = cur.fetchone()
        
        cur.execute("SELECT * FROM ats WHERE analysis_id = %s", (id,))
        ats_result = cur.fetchone()
        
        cur.execute("SELECT * FROM recruiter WHERE analysis_id = %s", (id,))
        recruiter_result = cur.fetchone()
        
        cur.execute("SELECT * FROM hiring_manager WHERE analysis_id = %s", (id,))
        hm_result = cur.fetchone()
        
        report = {
            "id": id,
            "role": role["employment_type"] if role else "Unknown", 
            "company": role["company_name"] if role else "Unknown", 
            "mode": mode["mode"] if mode else "Unknown",
            "final_result": {
                "ats_result": ats_result,
                "recruiter_result": recruiter_result,
                "hm_result": hm_result      
            }
        }
        
        return {
            "status": "success",
            "report": report
        }

    except Exception as error:
        raise error

    finally:
        cur.close()
        conn.close()
        
@app.post("/auth/signup")
def signup(user: UserCreate):
    conn, cur = get_db_connection()
    try:
        # Check if user exists
        cur.execute(GET_USER_BY_EMAIL_QUERY, (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Insert new user
        hashed_pw = get_password_hash(user.password)
        cur.execute(INSERT_USER_QUERY, (user.email, hashed_pw))
        new_user = cur.fetchone()
        conn.commit()
        return {"status": "success", "user_id": new_user["id"], "email": new_user["email"]}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn, cur = get_db_connection()
    try:
        cur.execute(GET_USER_BY_EMAIL_QUERY, (form_data.username,)) # OAuth2 uses 'username' for the email field
        user = cur.fetchone()
        
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)))
        access_token = create_access_token(
            data={"sub": str(user["id"])}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        if cur: cur.close()
        if conn: conn.close()