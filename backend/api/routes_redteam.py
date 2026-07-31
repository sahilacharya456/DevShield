from fastapi import APIRouter, Depends, BackgroundTasks
from backend.security.auth import get_pro_user
from pydantic import BaseModel
from backend.engine.redteam.red_agent import RedAgentEngine
import uuid

router = APIRouter()
engine = RedAgentEngine()

# Mock in-memory storage for jobs (simulate Celery backend for FYP)
job_store = {}

class RedagentRequest(BaseModel):
    target: str
    options: dict = {}

async def run_scan_task(job_id: str, req_data: dict):
    job_store[job_id] = {"status": "running"}
    try:
        result = await engine.run(req_data)
        job_store[job_id] = {"status": "completed", "result": result}
    except Exception as e:
        job_store[job_id] = {"status": "failed", "error": str(e)}

@router.post("/run")
async def run_module(req: RedagentRequest, background_tasks: BackgroundTasks, user=Depends(get_pro_user)):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_scan_task, job_id, req.model_dump())
    return {"status": "accepted", "job_id": job_id, "message": "RedAgent scan initiated. Processing in background."}

@router.get("/job/{job_id}")
async def get_job_status(job_id: str, user=Depends(get_pro_user)):
    job = job_store.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job
