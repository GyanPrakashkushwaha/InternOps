from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated, Optional, List
from pydantic import BaseModel, Field
import os
from .database import db_write_task

# Local Module Imports
from .models import (
    ATSAnalysis, 
    RecruiterAnalysis, 
    HiringManagerAnalysis, 
    JobMetadata, 
    ResumeMetaData, 
    MetaDataExtraction
)

from .prompts import (
    StrictCompliancePrompt, 
    RealWorldATSPrompt, 
    BrutalSignalPrompt, 
    ExtractionPrompt
)

from .services import gemini

# Structured LLM's
llm = gemini()
os.environ["LANGCHAIN_PROJECT"] = "virtual-recruiter"

# ***************************** STATES ***********************************
class InputState(TypedDict):
    resume_text: str
    job_description: str
    mode: Literal["strict", "real-world", "brutal"]
    
class ScreeningState(InputState):
    job_metadata: Optional[JobMetadata] = None
    resume_metadata: Optional[ResumeMetaData] = None
    ats_result: Optional[ATSAnalysis] = None
    recruiter_result: Optional[RecruiterAnalysis] = None
    hm_result: Optional[HiringManagerAnalysis] = None
    final_status: Literal["HIRE", "PENDING", "REJECT"]
    
class OutputState(BaseModel):
    job_metadata: Optional[JobMetadata] = None
    resume_metadata: Optional[ResumeMetaData] = None
    ats_result: Optional[ATSAnalysis] = Field(default=None, description="Result from ATS Agent")
    recruiter_result: Optional[RecruiterAnalysis] = Field(default=None, description="Result from Recruiter Agent")
    hm_result: Optional[HiringManagerAnalysis] = Field(default=None, description="Result from HM Agent")
    final_status: Literal["HIRE", "PENDING", "REJECT"] = "PENDING"


# Prompt Mapping
def get_prompt_class(mode: str):
    PROMPT_MAP = {
        "strict": StrictCompliancePrompt,
        "real-world": RealWorldATSPrompt,
        "brutal": BrutalSignalPrompt
    }
    return PROMPT_MAP.get(mode, RealWorldATSPrompt)

# Helper to format lists (e.g., skills) into strings for Prompts
def fmt_list(items: List[str]) -> str:
    return ", ".join(items) if items else "None"

# ***************************** NODE FUNCTIONS ***********************************

def extractor_agent_node(state: InputState):
    """
    Phase 1: Extracts structured JobMetadata from the raw Job Description text.
    """
    extractor_agent = llm.with_structured_output(MetaDataExtraction)
    
    # Ensure JobMetaDataExtractionPrompt is defined in your prompts.py, 
    # otherwise use a simple template here.
    agent_prompt = ExtractionPrompt.EXTRACTION_PROMPT.format(
        job_description = state["job_description"],
        resume_text = state["resume_text"]
    )
    
    response = extractor_agent.invoke(agent_prompt)
    return {"job_metadata": response.job_description, "resume_metadata": response.resume}

def ats_agent(state: ScreeningState):
    """
    Phase 2: ATS Agent. Uses structured metadata to enforce hard constraints.
    """
    ats_llm = llm.with_structured_output(ATSAnalysis)
    PromptClass = get_prompt_class(state["mode"])
    
    jd = state["job_metadata"]
    
    # We unpack the metadata and explicitly format lists to strings
    agent_prompt = PromptClass.ATS_PROMPT.format(
        resume_text=state["resume_text"],
        job_title=jd.job_title,
        company_name=jd.company_name,
        location=jd.location,
        work_mode=jd.work_mode,
        employment_type=jd.employment_type,
        min_education=jd.min_education,
        experience_level=jd.experience_level,
        required_skills=fmt_list(jd.required_skills),
        preferred_skills=fmt_list(jd.preferred_skills),
        job_summary=jd.job_summary
    )
    
    response = ats_llm.invoke(agent_prompt)
    return {"ats_result": response}
    
def recruiter_agent(state: ScreeningState):
    """
    Phase 3: Recruiter Agent. Checks culture fit, salary, and red flags.
    """
    recruiter_llm = llm.with_structured_output(RecruiterAnalysis)
    PromptClass = get_prompt_class(state["mode"])
    
    jd = state["job_metadata"]
    
    agent_prompt = PromptClass.RECRUITER_PROMPT.format(
        resume_text=state["resume_text"],
        ats_feedback=state["ats_result"].feedback,
        
        # Inject Recruiter specific context
        company_name=jd.company_name,
        department=jd.department,
        salary_range=jd.salary_range,
        company_overview=jd.company_overview,
        benefits=fmt_list(jd.benefits),
        work_mode=jd.work_mode,
        job_title=jd.job_title,
        experience_level=jd.experience_level
    )
    
    response = recruiter_llm.invoke(agent_prompt)
    return {"recruiter_result": response}

def hm_agent(state: ScreeningState):
    """
    Phase 4: Hiring Manager. Checks deep technical depth and specific duties.
    """
    hm_llm = llm.with_structured_output(HiringManagerAnalysis)
    PromptClass = get_prompt_class(state["mode"])
    
    jd = state["job_metadata"]
    
    agent_prompt = PromptClass.HM_PROMPT.format(
        resume_text=state["resume_text"],
        
        # Inject HM specific context
        reporting_to=jd.reporting_to,
        duties_responsibilities=fmt_list(jd.duties_responsibilities),
        required_skills=fmt_list(jd.required_skills),
        experience_level=jd.experience_level,
        department=jd.department
    )
    
    response = hm_llm.invoke(agent_prompt)
    return {"hm_result": response}
    
# ***************************** CONDITIONS & GRAPH ***********************************

def ats_condition(state: ScreeningState) -> Literal["PASS", "FAIL"]:
    # Fail fast if ATS rejects
    return state["ats_result"].decision

def recruiter_condition(state: ScreeningState) -> Literal["PASS", "FAIL"]:
    # Fail fast if Recruiter rejects
    return state["recruiter_result"].decision

# Graph Construction
builder = StateGraph(ScreeningState, input=InputState, output_schema=OutputState)

# 1. Add Nodes
builder.add_node("jd_extractor_node", extractor_agent_node)
builder.add_node("ats_node", ats_agent)
builder.add_node("recruiter_node", recruiter_agent)
builder.add_node("hm_node", hm_agent)

# 2. Add Edges
# Start -> Extract Metadata -> ATS
builder.add_edge(START, "jd_extractor_node")
builder.add_edge("jd_extractor_node", "ats_node")

# ATS -> (Pass) -> Recruiter -> (Pass) -> HM -> End
# ATS -> (Fail) -> End
builder.add_conditional_edges("ats_node", ats_condition, {"PASS": "recruiter_node", "FAIL": END})
builder.add_conditional_edges("recruiter_node", recruiter_condition, {"PASS": "hm_node", "FAIL": END})
builder.add_edge("hm_node", END)

# Compile Workflow
workflow = builder.compile()


def analyze_task(resume_text: str, job_description: str, mode: str, hash_key, analysis_id):
    
    try:
        input_state = {
            "resume_text": resume_text,
            "job_description": job_description,
            "mode": mode
        }
        
        output_state = workflow.invoke(input_state)
        
        output_state_dict = {
            "job_metadata": output_state["job_metadata"].model_dump(),
            "resume_metadata": output_state["resume_metadata"].model_dump(),
            "ats_result": output_state["ats_result"].model_dump()
        }
        if "recruiter_result" in output_state:
            output_state_dict["recruiter_result"] = output_state["recruiter_result"].model_dump()

        if "hm_result" in output_state:
            output_state_dict["hm_result"] = output_state["hm_result"].model_dump()
        
        print("================================ SAVING OUTPUT========================================")
        db_write_task(analysis_id, output_state_dict)
        print("================================ SAVING OUTPUT========================================")
    except Exception as e:
        raise e
        
    return output_state_dict