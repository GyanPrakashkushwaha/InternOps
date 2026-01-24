import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from .database_queries import (
    DB_CREATION_QUERY, 
    JOB_METADATA_INSERTION_QUERY,
    RESUME_METADATA_INSERTION_QUERY,
    ATS_RESULT_INSERTION_QUERY,
    RECRUITER_RESULT_INSERTION_QUERY,
    HM_RESULT_INSERTION_QUERY
)
import json

load_dotenv()

def get_db_uri():
    # Vercel / Neon / Railway standard environment variables
    # Priority: POSTGRES_URL -> DATABASE_URL -> Local Fallback
    return os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL") or "postgresql://postgres:password@localhost:5432/internops"

def get_db_connection():
    conn = None
    cur = None
    try:
        DB_URI = get_db_uri()
        # Vercel Postgres requires SSL mode
        ssl_mode = "require" if "localhost" not in DB_URI else "disable"
        
        conn = psycopg2.connect(DB_URI, sslmode=ssl_mode)
        cur = conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        raise RuntimeError(f"DB connection failed: {e}")
    return conn, cur

def init_db():
    conn = None
    cur = None
    try:
        conn, cur = get_db_connection()
        if not conn: raise RuntimeError("Database connection is None")
        cur.execute(DB_CREATION_QUERY)
        conn.commit()
    except Exception:
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_final_result(analysis_id):
    try:
        conn, cur = get_db_connection()
        query = "SELECT * FROM ats WHERE analysis_id = %s;"
        cur.execute(query, (analysis_id,))
        ats_result_tuple = cur.fetchone()
        
        ats_result = {}
        if ats_result_tuple:
            ats_result = {
                "match_score": ats_result_tuple["match_score"],
                "missing_keywords": ats_result_tuple["missing_keywords"],
                "formatting_issues": ats_result_tuple["formatting_issues"],
                "decision": ats_result_tuple["decision"],
                "feedback": ats_result_tuple["feedback"],
            }
        
        if ats_result and ats_result.get("decision") == "PASS":
            query = "SELECT * FROM recruiter WHERE analysis_id = %s;"
            cur.execute(query, (analysis_id,))
            recruiter_result_tuple = cur.fetchone()

            recruiter_result = {
                "career_progression_score": recruiter_result_tuple["career_progression_score"],
                "red_flags": recruiter_result_tuple["red_flags"],
                "soft_skills_detected": recruiter_result_tuple["soft_skills"],
                "decision": recruiter_result_tuple["decision"],
                "feedback": recruiter_result_tuple["feedback"],
            }
            
            if recruiter_result.get("decision") == "PASS":
                query = "SELECT * FROM hiring_manager WHERE analysis_id = %s;"
                cur.execute(query, (analysis_id,))
                hm_result_tuple = cur.fetchone()

                hm_result = {
                    "tech_depth_score": hm_result_tuple["tech_depth_score"],
                    "project_impact_score": hm_result_tuple["project_impact_score"],
                    "stack_alignment": hm_result_tuple["stack_alignment"],
                    "decision": hm_result_tuple["decision"],
                    "feedback": hm_result_tuple["feedback"],
                }
                
                return {
                    "ats_result": ats_result,
                    "recruiter_result": recruiter_result,
                    "hm_result": hm_result
                }
                
            return {
                "ats_result": ats_result,
                "recruiter_result": recruiter_result
            }
            
        return {
            "ats_result": ats_result
        }
        
    except Exception as e:
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()

def db_write_task(analysis_id: int, results: dict):
    """
    Synchronous DB write function.
    Previously executed by Celery, now called directly after analysis.
    """
    conn, cur = get_db_connection()
    try:
        meta = results["job_metadata"]
        
        cur.execute(JOB_METADATA_INSERTION_QUERY, (
            analysis_id,
            meta["job_title"],
            meta["company_name"],
            meta["location"],
            meta["employment_type"],
            meta["salary_range"],
            
            meta["department"],
            meta["reporting_to"],
            meta["job_summary"],
            meta["company_overview"],
            
            meta["experience_level"],
            meta["min_education"],
            meta["work_mode"],
            
            meta["required_skills"],       
            meta["preferred_skills"],      
            meta["duties_responsibilities"], 
            meta["benefits"]               
        ))
        
        res_meta = results["resume_metadata"]
        cur.execute(RESUME_METADATA_INSERTION_QUERY, (
            analysis_id,
            res_meta["full_name"],
            res_meta["email"],
            res_meta["phone"],
            res_meta["location"],
            
            res_meta["linkedin_url"],
            res_meta["github_url"],
            res_meta["summary"],
            res_meta["total_years_experience"],

            json.dumps(res_meta["education"]),
            json.dumps(res_meta["work_experience"]),
            json.dumps(res_meta["skills"]),
            json.dumps(res_meta["projects"]),
            
            json.dumps(res_meta["certifications"]),
            json.dumps(res_meta["awards"]),
            json.dumps(res_meta["volunteer_experience"]),
            res_meta["interests"]
        ))
        
        ats_result = results["ats_result"]
        cur.execute(ATS_RESULT_INSERTION_QUERY, 
                    (analysis_id, 
                    ats_result["match_score"], 
                    ats_result["missing_keywords"], 
                    ats_result["formatting_issues"], 
                    ats_result["decision"], 
                    ats_result["feedback"]))
     
        if "recruiter_result" in results:
            recruiter_result = results["recruiter_result"]
            cur.execute(RECRUITER_RESULT_INSERTION_QUERY, 
                        (analysis_id, 
                        recruiter_result["career_progression_score"], 
                        recruiter_result["red_flags"], 
                        recruiter_result["soft_skills_detected"], 
                        recruiter_result["decision"], 
                        recruiter_result["feedback"]))
            
        if "hm_result" in results:
            hm_result = results["hm_result"]
            cur.execute(HM_RESULT_INSERTION_QUERY, 
                        (analysis_id, 
                        hm_result["tech_depth_score"], 
                        hm_result["project_impact_score"], 
                        hm_result["stack_alignment"], 
                        hm_result["decision"], 
                        hm_result["feedback"]))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()