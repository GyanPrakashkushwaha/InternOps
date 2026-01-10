from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from langchain_core.prompts import ChatPromptTemplate

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
    
class LatexCodeAnalysis(BaseModel):
    decision: Literal["CORRECT", "NEEDS_IMPROVEMENT"] = Field(..., description="...")
    feedback: str = Field(..., description= "...")
