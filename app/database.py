
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DB_CREATION_QUERY = """
            ALTER DATABASE internops SET TIMEZONE TO 'Asia/Kolkata';
            CREATE TABLE IF NOT EXISTS analysis (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                hash_key TEXT NOT NULL,
                job_description TEXT,
                resume_text TEXT,
                mode VARCHAR, 
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS ats (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                analysis_id INT,
                match_score INT,
                missing_keywords TEXT[],
                formatting_issues TEXT[],
                decision VARCHAR NOT NULL,
                feedback TEXT NOT NULL,
                CONSTRAINT FK_atsTable_analysisId 
                FOREIGN KEY (analysis_id) 
                REFERENCES analysis(id)
                ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS recruiter (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                analysis_id INT,
                career_progression_score INT,
                red_flags TEXT[],
                soft_skills TEXT[],
                decision VARCHAR NOT NULL,
                feedback TEXT NOT NULL,
                CONSTRAINT FK_recruiterTable_analysisId                 
                FOREIGN KEY (analysis_id) 
                REFERENCES analysis(id)
                ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS hiring_manager (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                analysis_id INT ,
                tech_depth_score INT,
                project_impact_score INT,
                stack_alignment TEXT,
                decision VARCHAR NOT NULL,
                feedback TEXT NOT NULL,
                CONSTRAINT FK_hmTable_analysisId 
                FOREIGN KEY (analysis_id) 
                REFERENCES analysis(id)
                ON DELETE CASCADE
            );
        """

def get_db_connection():
    conn = None
    try:
        db_params = {
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "password"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5430"),
            "database": os.getenv("DB_NAME", "internops")
        }
        print(db_params)
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
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
