import uuid
from typing import Dict, Any

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.store.base import BaseStore
from langgraph.checkpoint.base import BaseCheckpointSaver

from .services import gemini

# Initialize model once
model = gemini()

async def call_model(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    
    user_id = config["configurable"]["user_id"]
    namespace = ("memories", user_id)
    
    # 1. Search Memory
    last_message = state["messages"][-1]
    memories = await store.asearch(namespace, query=str(last_message.content), limit=5)
    # print("\n\n\n\n\n ================================================= MEMORIES =================================================")
    # print(memories)
    # print("================================================= MEMORIES =================================================\n\n\n\n\n")
    memory_context = "\n".join([d.value["data"] for d in memories]) if memories else "No prior memories."
    
    system_msg = f"You are a helpful career assistant for InternOps. User context: {memory_context}"

    # 2. Save Memory (Triggered by keyword 'remember' for now, or use an LLM tool call)
    if "remember" in str(last_message.content).lower():
        # Store the user's message as a memory
        await store.aput(
            namespace, 
            str(uuid.uuid4()), 
            {"data": str(last_message.content)}
        )

    # 3. Invoke Model
    response = await model.ainvoke(
        [{"role": "system", "content": system_msg}] + state["messages"]
    )
    return {"messages": response}

def build_chat_graph(checkpointer: BaseCheckpointSaver, store: BaseStore):
    """Compiles and returns the StateGraph"""
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_edge(START, "call_model")
    
    return builder.compile(
        checkpointer=checkpointer,
        store=store
    )