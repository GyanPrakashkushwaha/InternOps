
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated, Optional
from operator import add
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

# Local Module Imports
from models import ATSAnalysis, RecruiterAnalysis, HiringManagerAnalysis, Prompt
from services import gemini

# Structured LLM's
llm = gemini()

# State
class ResumeScreeningState(TypedDict):
    resume_text: str
    job_description: str
    ats_result: Optional[ATSAnalysis] = None
    recruiter_result: Optional[RecruiterAnalysis] = None
    hm_result: Optional[HiringManagerAnalysis] = None
    final_status: Literal["HIRE", "PENDING", "REJECT"]

# Node Functions
def ats_agent(state: ResumeScreeningState):
    ats_llm = llm.with_structured_output(ATSAnalysis)
    agent_prompt = Prompt.ATS_PROMPT.format(
        resume_text = state["resume_text"],
        job_description = state["job_description"]
    )
    response = ats_llm.invoke(agent_prompt)
    return {"ats_result": response}
    
def recruiter_agent(state: ResumeScreeningState):
    recruiter_llm = llm.with_structured_output(RecruiterAnalysis)
    agent_prompt = Prompt.RECRUITER_PROMPT.format(
        resume_text = state["resume_text"],
        ats_feedback = state["ats_result"].feedback
    )
    response = recruiter_llm.invoke(agent_prompt)
    return {"recruiter_result": response}

def hm_agent(state: ResumeScreeningState):
    hm_llm = llm.with_structured_output(HiringManagerAnalysis)
    agent_prompt = Prompt.HM_PROMPT.format(
        resume_text = state["resume_text"],
        job_description = state["job_description"]
    )
    response = hm_llm.invoke(agent_prompt)
    return {"hm_result": response}
    
# conditional Functions
def ats_condition(state: ResumeScreeningState)-> Literal["PASS", "FAIL"]:
    if state["ats_result"].decision == "PASS":
        return "PASS"
    return "FAIL"

def recruiter_condition(state: ResumeScreeningState)-> Literal["PASS", "FAIL"]:
    return state["recruiter_result"].decision

# FIXME: add Try-Except block for robustness
# Graph
builder = StateGraph(ResumeScreeningState)

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