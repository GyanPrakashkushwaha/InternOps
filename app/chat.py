

from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash-lite")

# node functions
def bot_node(state: MessagesState):
    res = llm.invoke(state["messages"])
    return {"answer": res.content}

# GRAPH
builder = StateGraph(BotState)

# NODE
builder.add_node("bot", bot_node)

# EDGEs
builder.add_edge(START, "bot")
builder.add_edge("bot", END)