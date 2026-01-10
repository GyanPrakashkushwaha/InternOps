from celery import Celery
import json
import hashlib
from .recruiter import workflow
from .database import get_db_connection
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

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

@celery_app.task(bind=True)
def analyze_task(self, resume_text: str, job_description: str, mode: str):
    
    resume_hash = generate_hash(resume_text)
    jd_hash = generate_hash(job_description)
    cache_key = f"{resume_hash}_{jd_hash}_{mode}"

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT result FROM analysis_results WHERE id = %s",
        (cache_key,)
    )
    row = cur.fetchone()
    if row:
        cur.close()
        conn.close()
        print("Returning cached result from DB")
        return json.loads(row["result"])

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

    if "final_status" in output_state:
        output_state_dict["final_status"] = output_state["final_status"].model_dump()
    serialized_output = json.dumps(output_state_dict, default=str)

    # Insert / update cache
    query = """
    INSERT INTO analysis_results (id, resume_hash, jd_hash, mode, result)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (id)
    DO UPDATE SET
        resume_hash = EXCLUDED.resume_hash,
        jd_hash = EXCLUDED.jd_hash,
        mode = EXCLUDED.mode,
        result = EXCLUDED.result;
    """
    cur.execute(
        query,
        (cache_key, resume_text, job_description, mode, serialized_output)
    )
    conn.commit()
    cur.close()
    conn.close()

    return output_state_dict


