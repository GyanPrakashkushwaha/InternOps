

CREATE_USER_QUERY = """
INSERT INTO users (email, hashed_password)
VALUES
(%s, %s)
RETURNING id
"""

ANALYSIS_HISTORY_QUERY = """
SELECT 
	a.id as id, 
	jam.job_title as role, 
	jam.company_name as company, 
	a.created_at as date, 
	ham.decision as status
FROM analysis a
JOIN job_metadata jam
ON jam.analysis_id = a.id
LEFT JOIN recruiter r
ON r.analysis_id = r.id
LEFT JOIN hiring_manager ham
ON ham.analysis_id = a.id
ORDER BY a.created_at DESC
"""


# Fetch all the candiates details who did analysis and does not matter whether passed or failed ATS and went ahead.
DASHBOARD_HISTORY_QUERY = """
        SELECT 
            a.id as id,
            a.created_at as date,
            a.mode as mode, 
            ats.match_score as match_score, 
            ats.missing_keywords as missing_keywords,
            hm.decision as status,
            
            jam.job_title as job_title,
            jam.company_name as company_name,
            jam.location as location,
            jam.salary_range as salary_range,
            jam.work_mode as work_mode,
            jam.required_skills as required_skills,
            
            hm.tech_depth_score as tech_depth_score, 
            r.career_progression_score as career_progression_score, 
            SUBSTRING(hm.stack_alignment, 1, 7) as stack_alignment,
            r.soft_skills as soft_skills
            
        FROM analysis a
        JOIN ats
        ON ats.analysis_id = a.id
        JOIN job_metadata jam
        ON jam.analysis_id = a.id
        LEFT JOIN recruiter r
        ON r.analysis_id = a.id
        LEFT JOIN hiring_manager hm
        ON hm.analysis_id = a.id

        ORDER BY date DESC

"""
        
ANALYSIS_TABLE_INSERTION_QUERY = """
        INSERT INTO analysis (hash_key, job_description, resume_text, mode)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """

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
            
            CREATE TABLE IF NOT EXISTS users(
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
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

JOB_METADATA_INSERTION_QUERY = """
        INSERT INTO job_metadata (
            analysis_id, 
            job_title, company_name, location, employment_type, salary_range,
            department, reporting_to, job_summary, company_overview,
            experience_level, min_education, work_mode,
            required_skills, preferred_skills, duties_responsibilities, benefits
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
RESUME_METADATA_INSERTION_QUERY = """
        INSERT INTO resume_parsed_data (
            analysis_id,
            full_name, email, phone, location, 
            linkedin_url, github_url, summary, total_years_experience,
            education, work_experience, skills, projects,
            certifications, awards, volunteer_experience, interests
        )
        VALUES (
            %s, 
            %s, %s, %s, %s, 
            %s, %s, %s, %s,
            %s, %s, %s, %s, 
            %s, %s, %s, %s
        )
        """
        
ATS_RESULT_INSERTION_QUERY = """
        INSERT INTO ats (analysis_id, match_score, missing_keywords, formatting_issues, decision, feedback)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
RECRUITER_RESULT_INSERTION_QUERY = """
            INSERT INTO recruiter (analysis_id, career_progression_score, red_flags, soft_skills, decision, feedback)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        
HM_RESULT_INSERTION_QUERY = """
            INSERT INTO hiring_manager (analysis_id, tech_depth_score, project_impact_score, stack_alignment, decision, feedback)
            VALUES (%s, %s, %s, %s, %s, %s)
            """