import json
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from worker import run_research_task, celery_app

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
    
    while not task.ready():
        # Check task state
        if task.state == 'PROGRESS':
            # task.info contains the metadata from self.update_state()
            current_message = task.info.get("message", "")
            if current_message != last_message:
                yield emit(task.info)
                last_message = current_message
        
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
async def api_research(question: str = Query(..., min_length=3)):
    """
    Endpoint for the frontend to connect via EventSource.
    Yields Server-Sent Events (SSE) detailing the research progress.
    """
    # 1. Dispatch the task to Celery instantly
    task = run_research_task.delay(question)
    
    # 2. Return the SSE stream that polls the task progress
    return EventSourceResponse(celery_task_generator(task.id))

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
