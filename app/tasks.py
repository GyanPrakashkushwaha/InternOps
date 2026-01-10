from celery import Celery
import json
from .recruiter import workflow
from .utils import hashlib
from .database import get_db_connection
from .models import ATSAnalysis, RecruiterAnalysis, HiringManagerAnalysis
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Configure Celery to use Redis as the broker
celery_app = Celery(
    "internops_worker",
    broker=redis_url,
    backend=redis_url
)

@celery_app.task(bind=True)
def db_write_task(self, analysis_id: int, results: dict):
    conn, cur = get_db_connection()
    try:
        ats_result = results["ats_result"]
        ats_query = """
        INSERT INTO ats (analysis_id, match_score, missing_keywords, formatting_issues, decision, feedback)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(ats_query, 
                    (analysis_id, 
                    ats_result["match_score"], 
                    ats_result["missing_keywords"], 
                    ats_result["formatting_issues"], 
                    ats_result["decision"], 
                    ats_result["feedback"]))
        
        if "recruiter_result" in results:
            recruiter_result = results["recruiter_result"]
            recruiter_query = """
            INSERT INTO recruiter (analysis_id, career_progression_score, red_flags, soft_skills, decision, feedback)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(recruiter_query, 
                        (analysis_id, 
                        recruiter_result["career_progression_score"], 
                        recruiter_result["red_flags"], 
                        recruiter_result["soft_skills_detected"], 
                        recruiter_result["decision"], 
                        recruiter_result["feedback"]))
            
        if "hm_result" in results:
            hm_result = results["hm_result"]
            hm_query = """
            INSERT INTO hiring_manager (analysis_id, tech_depth_score, project_impact_score, stack_alignment, decision, feedback)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(hm_query, 
                        (analysis_id, 
                        hm_result["tech_depth_score"], 
                        hm_result["project_impact_score"], 
                        hm_result["stack_alignment"], 
                        hm_result["decision"], 
                        hm_result["feedback"]))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@celery_app.task(bind=True)
def analyze_task(self, resume_text: str, job_description: str, mode: str, hash_key, analysis_id):
    
    try:
        input_state = {
            "resume_text": resume_text,
            "job_description": job_description,
            "mode": mode
        }
        
        output_state = workflow.invoke(input_state)
        
        output_state_dict = {
            "ats_result": output_state["ats_result"].model_dump()
        }
        if "recruiter_result" in output_state:
            output_state_dict["recruiter_result"] = output_state["recruiter_result"].model_dump()

        if "hm_result" in output_state:
            output_state_dict["hm_result"] = output_state["hm_result"].model_dump()
            
        db_write_task.delay(analysis_id, output_state_dict)
    except Exception as e:
        raise e
        
    return output_state_dict