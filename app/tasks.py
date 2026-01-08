
from celery import Celery
import sqlite3
import json
import hashlib
from .main import workflow

# Configure Celery to use Redis as the broker
celery_app = Celery(
    "internops_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

DB_FILE = "analysis_cache.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id TEXT PRIMARY KEY,
            resume_hash TEXT,
            jd_hash TEXT,
            mode TEXT,
            result JSON,  -- Column name is 'result'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB on start
init_db()

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

@celery_app.task(bind=True)
def analyze_task(self, resume_text: str, job_description: str, mode: str):
    # 1. Generate unique hashes for inputs
    resume_hash = generate_hash(resume_text)
    jd_hash = generate_hash(job_description)
    cache_key = f"{resume_hash}_{jd_hash}_{mode}"

    # 2. Check SQLite Cache (Result Caching)
    conn = get_db_connection()
    cached_row = conn.execute(
        "SELECT result FROM analysis_results WHERE id = ?", (cache_key,)
    ).fetchone()
    
    if cached_row:
        conn.close()
        print("Returning cached result from SQLite")
        # Returns a Dictionary
        return json.loads(cached_row["result"])

    # 3. Run Workflow (If not cached)
    input_state = {
        "resume_text": resume_text,
        "job_description": job_description,
        "mode": mode
    }
    
    # LLM caching (Redis) happens automatically inside here due to services.py
    output_state = workflow.invoke(input_state)
    
    # the ats will always give result. so no need to check for ATS result.
    output_state_dict = {}
    output_state_dict["ats_result"] = output_state["ats_result"].model_dump()
    if "recruiter_result" in output_state:
        output_state_dict["recruiter_result"] = output_state["recruiter_result"].model_dump()
    if "hm_result" in output_state:
        output_state_dict["hm_result"] = output_state["hm_result"].model_dump()
    if "final_status" in output_state:
        output_state_dict["final_status"] = output_state["final_status"].model_dump()
        
    # We use default=str to handle Pydantic objects or datetime objects
    serialized_output = json.dumps(output_state_dict, default=str)

    # 4. Save to SQLite
    # FIXED: Table name 'analysis_results', Column name 'result'
    conn.execute(
        "INSERT OR REPLACE INTO analysis_results (id, resume_hash, jd_hash, mode, result) VALUES (?, ?, ?, ?, ?)",
        (cache_key, resume_hash, jd_hash, mode, serialized_output)
    )
    conn.commit()
    conn.close()
    
    # FIXED: Return the original dictionary (output_state), not the string.
    # This ensures consistency with the 'cached_row' return above.
    return output_state_dict
