
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated, Optional
from pydantic import BaseModel, Field
import os

# Local Module Imports
from .models import ATSAnalysis, RecruiterAnalysis, HiringManagerAnalysis
from .prompts import StrictCompliancePrompt, RealWorldATSPrompt, BrutalSignalPrompt

from .services import gemini

# Structured LLM's
llm = gemini()
os.environ["LANGCHAIN_PROJECT"] = "virtual-recruiter"
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# ***************************** STATES ***********************************
class InputState(TypedDict):
    resume_text: str
    job_description: str
    mode: Literal["strict", "real-world", "brutal"]
    
class ScreeningState(InputState):
    ats_result: Optional[ATSAnalysis] = None
    recruiter_result: Optional[RecruiterAnalysis] = None
    hm_result: Optional[HiringManagerAnalysis] = None
    final_status: Literal["HIRE", "PENDING", "REJECT"]
    
class OutputState(BaseModel):
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

# Node Functions
def ats_agent(state: InputState):
    ats_llm = llm.with_structured_output(ATSAnalysis)
    PromptClass = get_prompt_class(state["mode"])
    agent_prompt = PromptClass.ATS_PROMPT.format(
        resume_text = state["resume_text"],
        job_description = state["job_description"]
    )
    response = ats_llm.invoke(agent_prompt)
    return {"ats_result": response}
    
def recruiter_agent(state):
    recruiter_llm = llm.with_structured_output(RecruiterAnalysis)
    PromptClass = get_prompt_class(state["mode"])
    agent_prompt = PromptClass.RECRUITER_PROMPT.format(
        resume_text = state["resume_text"],
        ats_feedback = state["ats_result"].feedback
    )
    response = recruiter_llm.invoke(agent_prompt)
    return {"recruiter_result": response}

def hm_agent(state: InputState):
    hm_llm = llm.with_structured_output(HiringManagerAnalysis)
    PromptClass = get_prompt_class(state["mode"])
    agent_prompt = PromptClass.HM_PROMPT.format(
        resume_text = state["resume_text"],
        job_description = state["job_description"]
    )
    response = hm_llm.invoke(agent_prompt)
    return {"hm_result": response}
    
# conditional Functions
def ats_condition(state: ScreeningState)-> Literal["PASS", "FAIL"]:
    return state["ats_result"].decision

def recruiter_condition(state: ScreeningState)-> Literal["PASS", "FAIL"]:
    return state["recruiter_result"].decision

# FIXME: add Try-Except block for robustness
# Graph
builder = StateGraph(ScreeningState, input = InputState, output_schema= OutputState)

# Nodes
builder.add_node("ats_node", ats_agent)
builder.add_node("recruiter_node", recruiter_agent)
builder.add_node("hm_node", hm_agent)

# Edges
builder.add_edge(START, "ats_node")
builder.add_conditional_edges("ats_node", ats_condition,{"PASS": "recruiter_node", "FAIL": END})
builder.add_conditional_edges("recruiter_node", recruiter_condition, {"PASS": "hm_node", "FAIL": END})
builder.add_edge("hm_node", END)

# Workflow
workflow = builder.compile()


