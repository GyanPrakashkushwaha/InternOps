from pydantic import BaseModel, Field
from typing import List, Optional, Literal,Dict

# --- Section Models ---

class EducationItem(BaseModel):
    institution: str = Field(..., description="Name of the university or school.")
    degree: str = Field(..., description="Degree obtained (e.g., 'B.Tech', 'Master of Science').")
    field_of_study: str = Field(default="", description="Major or specialization.")
    location: str = Field(default="", description="City, Country.")
    start_date: str = Field(..., description="Start date (e.g., '2019').")
    end_date: str = Field(..., description="End date or 'Present'.")
    grade: Optional[str] = Field(None, description="GPA, CGPA, or Percentage if listed.")

class WorkExperienceItem(BaseModel):
    role: str = Field(..., description="Job title.")
    company: str = Field(..., description="Name of the company.")
    location: str = Field(default="Remote", description="City, Country or 'Remote'.")
    start_date: str = Field(..., description="Start date.")
    end_date: str = Field(..., description="End date or 'Present'.")
    description_bullets: List[str] = Field(..., description="Achievements and responsibilities.")
    tech_stack: List[str] = Field(default=[], description="Tools/Languages used in this specific role.")

class ProjectItem(BaseModel):
    name: str = Field(..., description="Project name.")
    description: str = Field(..., description="Brief summary.")
    tech_stack: List[str] = Field(..., description="Technologies used.")
    url: Optional[str] = Field(None, description="Link to code or demo.")
    bullets: List[str] = Field(default=[], description="Key outcomes or features.")

class CertificationItem(BaseModel):
    name: str = Field(..., description="Name of the certification (e.g., 'AWS Certified Solutions Architect').")
    issuer: str = Field(default="", description="Organization (e.g., 'Amazon', 'Google').")
    date: Optional[str] = Field(None, description="Date obtained or expiry.")

class VolunteerItem(BaseModel):
    role: str = Field(..., description="Role title (e.g., 'Mentor', 'Volunteer').")
    organization: str = Field(..., description="Organization name.")
    description: Optional[str] = Field(None, description="Brief description of impact.")

class AwardItem(BaseModel):
    title: str = Field(..., description="Name of the award or honor.")
    issuer: str = Field(default="", description="Who gave the award.")
    date: Optional[str] = Field(None, description="Date received.")

# --- Main Resume Extraction Model ---

class ResumeMetaData(BaseModel):
    # 1. Contact Information
    full_name: str = Field(..., description="Candidate's full name.")
    email: str = Field(..., description="Email address.")
    phone: str = Field(default="", description="Phone number.")
    location: str = Field(default="", description="City, State/Country.")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL.")
    github_url: Optional[str] = Field(None, description="GitHub or Portfolio URL.")

    # 2. Summary/Objective
    summary: str = Field(default="", description="Professional summary or objective statement.")

    # 3. Work Experience
    work_experience: List[WorkExperienceItem] = Field(default=[], description="Professional history.")

    # 4. Technical Skills
    skills: Dict[str, List[str]] = Field(
        ..., 
        description="Skills categorized by type (e.g., {'Languages': ['Python'], 'Cloud': ['AWS']} )."
    )

    # 5. Education
    education: List[EducationItem] = Field(..., description="Educational background.")

    # --- Optional/Enhancing Sections ---
    
    # 6. Projects
    projects: List[ProjectItem] = Field(default=[], description="Personal or academic projects.")

    # 7. Certifications
    certifications: List[CertificationItem] = Field(default=[], description="Professional certifications.")

    # 8. Awards & Honors
    awards: List[AwardItem] = Field(default=[], description="Awards, hackathon wins, or honors.")

    # 9. Volunteer Experience
    volunteer_experience: List[VolunteerItem] = Field(default=[], description="Volunteering and community service.")

    # 10. Interests/Hobbies
    interests: List[str] = Field(default=[], description="List of personal interests or hobbies.")

    # --- Meta-Analysis (Computed Fields for Agents) ---
    total_years_experience: float = Field(..., description="Total years of professional experience.")


class JobMetadata(BaseModel):
    # --- Core Job Data ---
    job_title: str = Field(..., description="Official name of the position (e.g., 'Senior Backend Engineer').")
    company_name: str = Field(..., description="Name of the hiring entity.")
    location: str = Field(..., description="City e.g. Delhi, State e.g. Bangalore, or 'Remote'.")
    employment_type: Literal["Full-time", "Part-time", "Contract", "Internship", "Freelance", "Unknown"] = Field(..., description="Type of employment.")
    salary_range: str = Field(..., description="Extracted compensation (e.g., '$120k-$150k', '20 LPA', '₹20000/month'). Use 'Not Disclosed' if missing.")
    
    # --- Job Identification & Summary ---
    department: str = Field(default="Unknown", description="e.g., 'Engineering', 'Sales'.")
    reporting_to: str = Field(default="Unknown", description="Manager title (e.g., 'CTO', 'Engineering Manager').")
    job_summary: str = Field(..., description="A 3-4 sentence high-level overview of why the job exists.")
    company_overview: str = Field(default="", description="Brief mission or culture description.")

    # --- Structured Requirements ---
    experience_level: Literal["Entry", "Mid", "Senior", "Lead", "Executive", "Unknown"] = Field(..., description=" inferred seniority level.")
    min_education: str = Field(default="Not Specified", description="e.g., 'Bachelor’s in CS', 'Master’s'.")
    required_skills: List[str] = Field(..., description="List of MANDATORY technical or soft skills.")
    preferred_skills: List[str] = Field(default=[], description="Nice-to-have skills that make a candidate stand out.")
    
    # --- Duties & Conditions ---
    duties_responsibilities: List[str] = Field(..., description="List of essential functions or tasks.")
    work_mode: Literal["Remote", "On-Site", "Hybrid"] = Field(..., description="Working environment.")
    benefits: List[str] = Field(default=[], description="Perks like 'Health Insurance', 'Stock Options', 'Free Food'.")

class MetaDataExtraction(BaseModel):
    job_description: Optional[JobMetadata] = Field(description="Extract Job Metadata")
    resume: Optional[ResumeMetaData] = Field(description="Extract Resume Metadata")

class ATSAnalysis(BaseModel):
    match_score: int = Field(..., description="0-100 score based on keyword overlapping and hard constraints.")
    missing_keywords: List[str] = Field(..., description="Critical keywords from JD missing in Resume.")
    formatting_issues: List[str] = Field(..., description="Issues like complex tables, missing headers, or unparseable sections.")
    decision: Literal["PASS", "FAIL"] = Field(..., description="If score < 70 or hard constraints missing, FAIL.")
    feedback: str = Field(..., description="Actionable advice to improve ATS readability.")
    
class RecruiterAnalysis(BaseModel):
    career_progression_score: int = Field(..., description="0-100 score on logical role transitions.")
    red_flags: List[str] = Field(..., description="Gaps > 6 months, job hopping, or downgrades in titles.")
    soft_skills_detected: List[str] = Field(..., description="Communication, leadership, or teamwork mentioned.")
    decision: Literal["PASS", "FAIL"] = Field(..., description="Pass if no major red flags and clear progression.")
    feedback: str = Field(..., description="Advice on how the candidate presents their story.")

class HiringManagerAnalysis(BaseModel):
    tech_depth_score: int = Field(..., description="0-100. Do they use 'built/architected' vs 'used'?")
    project_impact_score: int = Field(..., description="0-100. Are there metrics ($, %, users, latency)?")
    stack_alignment: str = Field(..., description="How well their specific tech experience maps to the JD's stack.")
    decision: Literal["HIRE", "NO_HIRE", "MAYBE"]
    feedback: str = Field(..., description="Deep technical advice on improving bullet points.")

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : str or None = None

class User(BaseModel):
    email: str
    password: str
    
class UserInDB(User):
    hashed_password: str
