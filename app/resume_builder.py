
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Dict, Literal, Annotated
from operator import add
from pydantic import BaseModel
from prompts import ResumeBuilderPrompt
from services import gemini
from models import LatexCodeAnalysis

# BUG - Latex code not being generated as expected.
# FIXME - Use other gemini model and then try to generate the latex code.
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# state
class BuilderStateInput(TypedDict):
    resume_text : str
    analysis_result: Dict[str, str]
    
class BuilderGenerationState(BuilderStateInput):
    latex_resume_code: str
    latex_code_evaluations : Annotated[list[str], add]
    decision : Literal["CORRECT", "NEEDS_IMPROVEMENT"]
    
class BuilderStateOutput(TypedDict):
    latex_resume_code: str

llm = gemini(model="gemini-2.5-flash")

# Node Functions
def builder_node(state: BuilderStateInput):
    prompt = ResumeBuilderPrompt.BUILDER_PROMPT.format(
        resume_text = state["resume_text"],
        analysis_report_json = json.loads(state["analysis_result"])
    )
    response = llm.invoke(prompt)
    return {"latex_resume_code": response.content}

def evaluate_code(state: BuilderGenerationState):
    prompt = ResumeBuilderPrompt.EVALUATOR_PROMPT.format(
      latex_resume_code = state["latex_resume_code"]
    )
    response = llm.with_structured_output(LatexCodeAnalysis).invoke(prompt)
    return {"latex_code_evaluations": [response.feedback], "decision": response.decision}

# Conditional func
def evaluation_condition(state: BuilderGenerationState) -> Literal["CORRECT", "NEEDS_IMPROVEMENT"]:
    return state["decision"]  

# GRAPH
builder = StateGraph(BuilderGenerationState, input_schema= BuilderStateInput, output_schema = BuilderStateOutput)
# node
builder.add_node("builder_node", builder_node)
builder.add_node("evaluate_code", evaluate_code)

# edges
builder.add_edge(START, "builder_node")
builder.add_edge("builder_node", "evaluate_code")
builder.add_conditional_edges("evaluate_code", evaluation_condition, {"CORRECT": END, "NEEDS_IMPROVEMENT": "builder_node"})

workflow = builder.compile()
