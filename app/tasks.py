
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
    print("=================================================================== \n CACHE KEY \n =================================== \n\n ",cache_key, "\n \n=================================================================== \n CACHE KEY \n ===================================")
    

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
    
    # Clean up result for JSON serialization
    # We use default=str to handle Pydantic objects or datetime objects
    output = output_state
    serialized_output = json.dumps(output, default=str)

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
    return output_state


{
  "status": "completed",
  "data": {
    "ats_result": "match_score=85 missing_keywords=['LLaMA', 'Mistral', 'OpenAI', 'PEFT concepts', 'AI application architecture'] formatting_issues=['Resume contains special characters and unicode characters that may not be parsed correctly by all ATS systems.'] decision='PASS' feedback='The candidate has a strong match with many of the required skills, particularly in Generative AI concepts like RAG and prompt engineering. However, specific LLM technologies (OpenAI, LLaMA, Mistral) and advanced concepts like PEFT and AI application architecture are not explicitly mentioned in the resume. To improve the match, the candidate should consider adding these specific technologies and concepts to their resume, especially if they have experience with them. The resume also has some formatting issues with special characters that could hinder ATS parsing.'",
    "recruiter_result": "career_progression_score=90 red_flags=[] soft_skills_detected=['analytical thinking', 'problem-solving skills'] decision='PASS' feedback='The candidate has a strong academic background and relevant project experience in Data Science and Machine Learning. The resume highlights practical application of ML concepts and optimization techniques. While the ATS noted a lack of specific LLM technologies, the projects demonstrate a good understanding of RAG and pipeline development. The candidate should ensure consistent formatting for better ATS compatibility.'",
    "hm_result": "tech_depth_score=75 project_impact_score=60 stack_alignment='Good' decision='MAYBE' interview_questions=['Can you elaborate on your experience with fine-tuning LLMs? Specifically, what PEFT techniques have you used, and in what scenarios?', 'Describe a time you had to explain a complex AI concept (like RAG or LLM architecture) to someone with a non-technical background. What was your approach, and what was the outcome?', 'You mention optimizing TTFT by 90% with FastAPI and LangGraph. Can you walk me through the specific architectural changes you made to achieve this, and what trade-offs were involved?', 'How would you approach designing a new course module on prompt engineering for beginners, considering the rapid evolution of LLM capabilities?'] feedback=\"The candidate has a solid foundation in ML and has demonstrated practical application through their projects. Their experience with RAG pipelines, FastAPI, and MLflow is directly relevant. However, the resume lacks specific details on fine-tuning/PEFT techniques, which is a key requirement in the JD. While they mention 'building production-ready ML pipelines', the depth of their involvement in architectural decisions versus implementation needs further probing. The impact scores are moderate; quantifying achievements further (e.g., specific improvements in prediction accuracy, latency reduction percentages beyond the one mentioned) would strengthen their profile. The 'Stack Compliance' is good, with several key technologies aligning. The decision is a 'MAYBE' because while they have relevant experience, the depth in fine-tuning and architectural design needs to be verified in the interview.\""
  }
}

{
  "status": "completed",
  "data": {
    "ats_result": "match_score=85 missing_keywords=['LLaMA', 'Mistral', 'OpenAI', 'PEFT concepts', 'AI application architecture'] formatting_issues=['Resume contains special characters and unicode characters that may not be parsed correctly by all ATS systems.'] decision='PASS' feedback='The candidate has a strong match with many of the required skills, particularly in Generative AI concepts like RAG and prompt engineering. However, specific LLM technologies (OpenAI, LLaMA, Mistral) and advanced concepts like PEFT and AI application architecture are not explicitly mentioned in the resume. To improve the match, the candidate should consider adding these specific technologies and concepts to their resume, especially if they have experience with them. The resume also has some formatting issues with special characters that could hinder ATS parsing.'",
    "recruiter_result": "career_progression_score=90 red_flags=[] soft_skills_detected=['analytical thinking', 'problem-solving skills'] decision='PASS' feedback='The candidate has a strong academic background and relevant project experience in Data Science and Machine Learning. The resume highlights practical application of ML concepts and optimization techniques. While the ATS noted a lack of specific LLM technologies, the projects demonstrate a good understanding of RAG and pipeline development. The candidate should ensure consistent formatting for better ATS compatibility.'",
    "hm_result": "tech_depth_score=75 project_impact_score=60 stack_alignment='Good' decision='MAYBE' interview_questions=['Can you elaborate on your experience with fine-tuning LLMs? Specifically, what PEFT techniques have you used, and in what scenarios?', 'Describe a time you had to explain a complex AI concept (like RAG or LLM architecture) to someone with a non-technical background. What was your approach, and what was the outcome?', 'You mention optimizing TTFT by 90% with FastAPI and LangGraph. Can you walk me through the specific architectural changes you made to achieve this, and what trade-offs were involved?', 'How would you approach designing a new course module on prompt engineering for beginners, considering the rapid evolution of LLM capabilities?'] feedback=\"The candidate has a solid foundation in ML and has demonstrated practical application through their projects. Their experience with RAG pipelines, FastAPI, and MLflow is directly relevant. However, the resume lacks specific details on fine-tuning/PEFT techniques, which is a key requirement in the JD. While they mention 'building production-ready ML pipelines', the depth of their involvement in architectural decisions versus implementation needs further probing. The impact scores are moderate; quantifying achievements further (e.g., specific improvements in prediction accuracy, latency reduction percentages beyond the one mentioned) would strengthen their profile. The 'Stack Compliance' is good, with several key technologies aligning. The decision is a 'MAYBE' because while they have relevant experience, the depth in fine-tuning and architectural design needs to be verified in the interview.\""
  }
}

