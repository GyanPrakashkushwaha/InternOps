import json
import asyncio
from typing import Literal

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Internal Modules
from .utils import read_pdf, generate_hash
from .database import init_db, get_db_connection, get_final_result, create_new_user
from .analyze import analyze_task
from .database_queries import (
    DASHBOARD_HISTORY_QUERY,
    ANALYSIS_TABLE_INSERTION_QUERY,
    ANALYSIS_HISTORY_QUERY
)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .auth import verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from .database import get_user_by_email

from .models import (
    Token, TokenData, User, UserInDB
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
    job_description: str = Form(...)
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
        cur.execute(ANALYSIS_TABLE_INSERTION_QUERY, (hash_key, job_description, resume_content, mode))
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
def fetch_dashboard_history():
    try:
        conn, cur = get_db_connection()
        cur.execute(DASHBOARD_HISTORY_QUERY)
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


@app.get("/web/dashboard/history")
def fetch_dashboard_history(current_user: dict = Depends(get_current_user)):
    try:
        conn, cur = get_db_connection()
        cur.execute(DASHBOARD_HISTORY_QUERY)
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
        if cur: cur.close()
        if conn: conn.close()
        
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
        

@app.post("/signup")
def user_registration(user_details: User):
    # Accept a JSON body containing email and password. (Hint: Use a Pydantic model!)
    # Get a database connection (using your get_db_connection).
    # Call your create_new_user function.
    # Return a success message and the new user_id.
    
    conn, cur = get_db_connection()
    try:
        # print(user_details)
        user_id = create_new_user(conn, cur, user_details.email, str(user_details.password))
        # print(user_details.password)
        return {
            "message": "User Created Sucessfully!",
            "user-id": user_id
        }
    except Exception as e:
        raise e
    finally:
        conn.close()
        cur.close()
        
@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm maps the email field to 'username' behind the scenes
    user = get_user_by_email(form_data.username) 
    
    # Verify the user exists and the password matches
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
