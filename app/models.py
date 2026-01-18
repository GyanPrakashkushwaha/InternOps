from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from langchain_core.prompts import ChatPromptTemplate

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
    