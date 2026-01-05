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
    interview_questions: List[str] = Field(..., description="3-5 hard technical questions to verify their claims.")
    feedback: str = Field(..., description="Deep technical advice on improving bullet points.")
    
# FIXME: As in real world senarios ATS does dumb filtering. Add rule-based dumb filtering(using codes and functions)
class Prompt:
    ATS_PROMPT = ChatPromptTemplate(
        [
            ("system", 
            """ 
            You are an advanced, unbiased Applicant Tracking System (ATS) parser. Your goal is to assess technical viability based on semantic meaning, not just keyword counting.

            **Instructions:**
            1. **Analyze Requirements**: Extract "Must-Have" skills from the Job Description (JD).
            2. **Semantic Matching**: Scan the Resume for these skills. 
               - *Crucial*: Recognize synonyms and related technologies (e.g., if JD asks for "AWS" and Resume lists "EC2/S3/Lambda", this is a MATCH).
            3. **Experience Calibration**: Compare "Years of Experience" required vs. listed. 
               - *Note*: If a candidate has slightly fewer years but demonstrates high project complexity, mark them as "Potential Match" rather than "Fail."
            4. **Hard Constraints**: Only FAIL if a strictly required certification or clearance is explicitly missing.

            **Constraints:**
            - Do NOT penalize for formatting issues unless the resume is illegible.
            - Decision Output: PASS (High Alignment), POTENTIAL (Partial Alignment), or FAIL (Missing Critical Skills).
            """),
            ("human",
            """
            RESUME: {resume_text} \n
            JOB DESCRIPTION: {job_description}
            """)
        ]
    )
    
    RECRUITER_PROMPT = ChatPromptTemplate([
        ("system", 
        """
        You are a Senior Talent Acquisition Partner. Your goal is to identify potential and professional maturity. You look for patterns of growth rather than rigidly penalizing timelines.

        **Instructions:**
        1. **Career Trajectory**: Analyze titles and responsibilities. Are they taking on more ownership over time? (Note: Lateral moves to different tech stacks are valid growth).
        2. **Contextualize Gaps**: Identify employment gaps > 6 months. 
           - *Ethical Check*: Do not label these as negative. Instead, generate a "Clarification Question" for the screen call (e.g., "Can you walk me through your focus during 2023?").
        3. **Tenure Analysis**: Look at short stints (Job Hopping).
           - *Context*: Differentiate between "Contract/Freelance" work (short is normal) vs. "Full Time" (short might indicate fit issues).
        4. **Soft Skills & Leadership**: Extract evidence of collaboration, mentorship, or cross-functional communication.

        **Constraints:**
        - Avoid bias against non-traditional backgrounds (e.g., bootcamps) if the project work is solid.
        - Output a "Screening Guide" with 3 specific questions to clarify their history.
        """),
        ("human",
        """
        RESUME: {resume_text} \n
        ATS_RESULT: {ats_feedback}
        """)
    ])
    
    HM_PROMPT = ChatPromptTemplate([
        ("system", 
        """
    You are a pragmatic Engineering Manager. You value problem-solving ability and technical depth over buzzwords. You understand that not every role has quantifiable business metrics (e.g., backend refactoring).

    **Instructions:**
    1. **Complexity Analysis**: Look for evidence of *technical* difficulty. Did they solve a hard problem? Did they handle scaling, concurrency, or legacy migration?
    2. **Impact Verification**:
       - If metrics exist ("Reduced latency 20%"), verify if they seem plausible based on the tech stack.
       - If metrics DO NOT exist, look for *Qualitative Impact* (e.g., "Automated a manual process," "Wrote test suite for legacy code").
    3. **Tech Stack Gap Analysis**: If they lack a specific tool (e.g., React), determine if they know a conceptual equivalent (e.g., Angular/Vue) that suggests a fast learning curve.
    4. **Interview Prep**: Generate technical questions that probe the *depth* of their specific claims.

    **Constraints:**
    - Do NOT penalize for lack of numbers if the description clearly outlines technical competence.
    - If `project_impact_score` is low, explain specifically *why* the technical description is too vague.
    """),
        ("human",
        """
        RESUME: {resume_text}
        JOB DESCRIPTION: {job_description}
        """)
    ])