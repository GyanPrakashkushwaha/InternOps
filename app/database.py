
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

def get_db_uri():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

DB_CREATION_QUERY = """
            -- ALTER DATABASE internops_db SET TIMEZONE TO 'Asia/Kolkata';
            CREATE TABLE IF NOT EXISTS analysis (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                hash_key TEXT NOT NULL,
                job_description TEXT,
                resume_text TEXT,
                mode VARCHAR,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS resume_parsed_data (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                analysis_id INT UNIQUE,

                -- 1. Contact Information
                full_name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                phone VARCHAR,
                location VARCHAR,
                linkedin_url VARCHAR,
                github_url VARCHAR,
                portfolio_url VARCHAR,

                -- 2. Professional Summary
                summary TEXT,

                -- 3. Technical Skills
                -- Stored as JSONB to handle dynamic categories (e.g., {"Languages": ["Python"], "Cloud": ["AWS"]})
                skills JSONB DEFAULT '{}'::jsonb, 

                -- 4. Meta-Analysis
                total_years_experience NUMERIC(4,1), -- Allows values like 2.5, 10.0

                -- 5. Complex Nested Structures (JSONB Arrays of Objects)
                -- We use JSONB here because these are lists of rich objects (Start Date, End Date, Description), not just simple strings.
                education JSONB DEFAULT '[]'::jsonb,            -- Schema: List[EducationItem]
                work_experience JSONB DEFAULT '[]'::jsonb,      -- Schema: List[WorkExperienceItem]
                projects JSONB DEFAULT '[]'::jsonb,             -- Schema: List[ProjectItem]
                certifications JSONB DEFAULT '[]'::jsonb,       -- Schema: List[CertificationItem]
                awards JSONB DEFAULT '[]'::jsonb,               -- Schema: List[AwardItem]
                volunteer_experience JSONB DEFAULT '[]'::jsonb, -- Schema: List[VolunteerItem]

                -- 6. Simple Arrays
                interests TEXT[],

                -- System Fields
                parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT FK_resume_analysisId 
                    FOREIGN KEY (analysis_id) 
                    REFERENCES analysis(id)
                    ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS job_metadata (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                analysis_id INT UNIQUE,
                
                -- Core Identity
                job_title VARCHAR NOT NULL,
                company_name VARCHAR NOT NULL,
                location VARCHAR,
                employment_type VARCHAR,
                salary_range VARCHAR,
                
                -- Hierarchy & Context
                department VARCHAR,
                reporting_to VARCHAR,
                job_summary TEXT,
                company_overview TEXT,
                
                -- Filters (The "Structured Requirements")
                experience_level VARCHAR,
                min_education VARCHAR,
                work_mode VARCHAR,
                
                -- Arrays for Rich Data
                required_skills TEXT[],        -- Searchable!
                preferred_skills TEXT[],
                duties_responsibilities TEXT[],
                benefits TEXT[],
                
                -- System Fields
                posted_date DATE DEFAULT CURRENT_DATE,
                is_active BOOLEAN DEFAULT TRUE,

                CONSTRAINT FK_jobMeta_analysisId 
                    FOREIGN KEY (analysis_id) 
                    REFERENCES analysis(id)
                    ON DELETE CASCADE
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
    cur = None
    try:
        DB_URI = get_db_uri()
        conn = psycopg2.connect(DB_URI)
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
        query = """
        SELECT * FROM ats
        WHERE analysis_id = %s;
        """
        cur.execute(query, (analysis_id,))
        ats_result_tuple = cur.fetchone()
        ats_result = {}
        if ats_result_tuple:
            print(f"======================================= ATS RESULT {analysis_id}=================================================")
            print(ats_result_tuple)
            print("======================================= ATS RESULT =================================================")
            ats_result = {
                "match_score": ats_result_tuple["match_score"],
                "missing_keywords": ats_result_tuple["missing_keywords"],
                "formatting_issues": ats_result_tuple["formatting_issues"],
                "decision": ats_result_tuple["decision"],
                "feedback": ats_result_tuple["feedback"],
            }
        
        # data base can also be used to check if the entry exists or not.
        if ats_result and ats_result["decision"] == "PASS":
            query = """
            SELECT * FROM recruiter
            WHERE analysis_id = %s;
            """        
            cur.execute(query, (analysis_id,))
            recruiter_result_tuple = cur.fetchone()
            # print("======================================= RECRUITER RESULT =================================================")
            # print(recruiter_result_tuple)
            # print("======================================= RECRUITER RESULT =================================================")

            recruiter_result = {
                "career_progression_score": recruiter_result_tuple["career_progression_score"],
                "red_flags": recruiter_result_tuple["red_flags"],
                "soft_skills_detected": recruiter_result_tuple["soft_skills"],
                "decision": recruiter_result_tuple["decision"],
                "feedback": recruiter_result_tuple["feedback"],
            }
            
            if recruiter_result["decision"] == "PASS":
                query = """
                SELECT * FROM hiring_manager
                WHERE analysis_id = %s;
                """        
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
        cur.close()
        conn.close()
    return final_result