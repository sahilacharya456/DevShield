from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.worker import get_task_result, scan_supply_chain_manifest_task

router = APIRouter()


class SupplyChainScanJobRequest(BaseModel):
    manifest_name: str = Field(..., min_length=1, description="Manifest filename, e.g. requirements.txt or package-lock.json.")
    manifest_content: str = Field(..., min_length=1, description="Raw manifest contents.")


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Any | None = None
    error: str | None = None


@router.post("/scans/supply-chain", response_model=JobCreatedResponse)
async def enqueue_supply_chain_scan(payload: SupplyChainScanJobRequest):
    task = scan_supply_chain_manifest_task.delay(payload.manifest_name, payload.manifest_content)
    return JobCreatedResponse(job_id=task.id, status=task.status)


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    task = get_task_result(job_id)
    response = JobStatusResponse(job_id=job_id, status=task.status)

    if task.successful():
        response.result = task.result
    elif task.failed():
        response.error = str(task.result)

    return response
