import os
import json
import asyncio
import time
from fastapi import FastAPI, Query, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyQuery
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from worker import run_research_task, celery_app

API_KEY = os.getenv("BACKEND_API_KEY", "dev-secret-key")
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_query)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate API key")
    return api_key

app = FastAPI(title="Web Research Agent API")

# Add CORS so the frontend can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def celery_task_generator(task_id: str):
    """
    Polls the Celery task state from Redis and streams updates via SSE.
    """
    def emit(payload: dict):
        return json.dumps(payload)
        
    task = celery_app.AsyncResult(task_id)
    last_message = ""
    last_emit_time = time.time()
    
    # Emit the task_id immediately so the frontend can store it for cancellation
    yield emit({"status": "Started", "task_id": task_id})
    
    while not task.ready():
        # Check task state
        if task.state == 'PROGRESS':
            # task.info contains the metadata from self.update_state()
            current_message = task.info.get("message", "")
            if current_message != last_message:
                yield emit(task.info)
                last_message = current_message
                last_emit_time = time.time()
            elif time.time() - last_emit_time > 15:
                # Send a keep-alive ping to prevent Azure load balancer from dropping the connection
                yield emit({"status": "Heartbeat", "message": current_message})
                last_emit_time = time.time()
        
        # Sleep briefly before polling again to avoid spamming Redis
        await asyncio.sleep(0.5)
        
    # Task is finished (SUCCESS or FAILURE)
    if task.state == 'SUCCESS':
        result = task.result
        # The worker returns the final Complete payload
        yield emit(result)
    elif task.state == 'FAILURE':
        yield emit({"status": "Error", "error": str(task.result)})
    else:
        yield emit({"status": "Error", "error": f"Task ended with unknown state: {task.state}"})

@app.get("/api/research")
async def api_research(
    question: str = Query(..., min_length=3),
    api_key: str = Depends(verify_api_key)
):
    """
    Endpoint for the frontend to connect via EventSource.
    Yields Server-Sent Events (SSE) detailing the research progress.
    """
    # 1. Dispatch the task to Celery instantly
    task = run_research_task.delay(question)
    
    # 2. Return the SSE stream that polls the task progress
    return EventSourceResponse(celery_task_generator(task.id))

@app.post("/api/research/{task_id}/stop")
async def stop_research(
    task_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Cancel an ongoing research task.
    """
    try:
        celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')
        return {"status": "ok", "message": "Task terminated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

from database import get_research_logs

@app.get("/api/logs")
async def api_logs(
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """
    Fetch the history of generated research logs from the MongoDB database.
    """
    try:
        logs = await get_research_logs(limit=limit)
        return {"status": "ok", "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
