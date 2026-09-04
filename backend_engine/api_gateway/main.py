import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from celery import Celery

app = FastAPI(title="Backend Engine API Gateway")

# Configure Celery to connect to Redis
redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("gpu_tasks", broker=redis_url, backend=redis_url)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/mode-a/generate")
async def generate_avatar(
    weight: float = Form(...),
    height: float = Form(...),
    body_shape: str = Form(...)
):
    """
    Mode A: Generates parametric 3D avatar base meshes scaled via numerical inputs.
    """
    # Dispatch task to the GPU Worker
    task = celery_app.send_task(
        "worker.process_mode_a",
        args=[weight, height, body_shape]
    )
    return {"task_id": task.id, "status": "Task enqueued to GPU worker cluster"}

@app.post("/mode-b/warp")
async def warp_photo(file: UploadFile = File(...)):
    """
    Mode B: Photo-Realistic AR processing. 
    Image goes to ephemeral session, is processed, and then memory is purged.
    """
    raw_image_data = await file.read()
    session_token = str(uuid.uuid4())
    
    # In a real scenario, passing large binary data via message broker is an anti-pattern.
    # We would pass a reference to a secure, ephemeral blob store.
    # For this mock, we pass it to the worker simulating an isolated container session.
    
    task = celery_app.send_task(
        "worker.process_mode_b",
        args=[raw_image_data, session_token]
    )
    return {
        "task_id": task.id, 
        "status": "Image sent to ephemeral container session",
        "session_token": session_token
    }

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": "Pending or processing..."}
    elif task_result.state == "SUCCESS":
        return {"status": "SUCCESS", "result": task_result.result}
    elif task_result.state == "FAILURE":
        return {"status": "FAILURE", "error": str(task_result.info)}
    return {"status": task_result.state}
