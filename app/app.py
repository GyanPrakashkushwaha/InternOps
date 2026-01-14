
import json
import asyncio
from contextlib import asynccontextmanager
from typing import Literal, AsyncGenerator

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from base64 import b64encode
from langchain_core.messages import HumanMessage
from celery.result import AsyncResult
from psycopg_pool import AsyncConnectionPool

# LangGraph Persistence
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore

# Internal Modules
from .utils import read_pdf, generate_hash
from .database import init_db, get_db_connection, get_final_result, get_db_uri
from .tasks import celery_app, analyze_task
from .models import ChatRequest
from .chat import build_chat_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Sync DB Init (Legacy tables)
    print("--- 🟢 Startup: Initializing Legacy Tables ---")
    try:
        init_db() 
    except Exception as e:
        print(f"Warning: Sync DB Init failed: {e}")
    
    DB_URI = get_db_uri()
    async with AsyncConnectionPool(conninfo=DB_URI, max_size=20) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        store = AsyncPostgresStore(pool)
        
        # await checkpointer.setup()
        # await store.setup()
        
        app.state.graph = build_chat_graph(checkpointer, store)
        yield
    print("--- Closing DB Connection Pool ---")
    
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "Backend is running!"}


@app.post("/analyze/{mode}")
async def analysis(
    mode: Literal["strict", "real-world", "brutal"],
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_content = await read_pdf(file)
    conn, cur = get_db_connection()
    
    try:
        resume_hash = generate_hash(resume_content)
        jd_hash = generate_hash(job_description)
        hash_key = f"{resume_hash}_{jd_hash}_{mode}"
        
        # Check cache
        cur.execute("SELECT id FROM analysis WHERE hash_key = %s", (hash_key, ))
        existing_id = cur.fetchone()
        
        if existing_id:
            final_result = get_final_result(existing_id[0])
            return {"status": "Completed", "final_result": final_result, "analysis_id" : existing_id[0]}
        
        # Create new entry
        query = """
        INSERT INTO analysis (hash_key, job_description, resume_text, mode)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        cur.execute(query, (hash_key, job_description, resume_content, mode))
        analysis_id = cur.fetchone()[0]
        conn.commit()
        
        # Dispatch Celery Task
        task = analyze_task.delay(
            resume_text=resume_content, 
            job_description=job_description, 
            mode=mode, 
            hash_key=hash_key,
            analysis_id = analysis_id
        )
        
        return {
            "status": "Analysis Started",
            "task_id": task.id,
            "mode": mode,
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
        
        
@app.get("/analysis_result/{analysis_id}")
def get_analysis_result(analysis_id):
    final_result = get_final_result(analysis_id)
    # print(final_result)
    return {
            "status": "Completed",
            "final_result": final_result
        }

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        if result.successful():
            return {"status": "Completed", "final_result": result.get()}
        else:
            return {"status": "Failed", "error": str(result.result)}
    else:
        return {"status": "Processing"}
    

@app.get("/analysis_id_list")
def analysis_history():
    try:
        conn, cur = get_db_connection()
        query = """
        SELECT id FROM analysis
        """
        cur.execute(query)
        analysis_id = cur.fetchall()
        print(analysis_id)
        return {
            "status": "done",
            "id_list": analysis_id
        }
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()

@app.get("/get_chat_history/{thread_id}")
def get_chat_history(thread_id):
    pass

@app.post("/chat/stream/{user_id}/{analysis_id}")
async def stream_chat(request: ChatRequest, user_id, analysis_id):
    async def event_generator() -> AsyncGenerator[str, None]:
        config = {
            "configurable": {
                "thread_id": analysis_id,
                "user_id": user_id,
            }
        }
        try:
            async for event in app.state.graph.astream_events(
                {"messages": [HumanMessage(content=request.question)]},
                config=config,
                version="v2"
            ):
                kind = event["event"]
                
                # Capture generated tokens
                if kind == "on_chain_stream":
                    chunk = event["data"].get("chunk")
                    if chunk and "messages" in chunk:
                        payload = json.dumps({"token": chunk["messages"].content})
                        yield f"data: {payload}\n\n"
                
                # print(event)
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            print(f"Error streaming chat: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.on_event("startup")
def startup():
    init_db()