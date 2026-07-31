from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.services.project_service import ProjectService
from backend.services.scanner_service import ScannerService
from backend.security.auth import get_current_user
from backend.models.orm import User

router = APIRouter()

class CreateProjectRequest(BaseModel):
    name: str
    language: str
    repo_url: str = ""

@router.get("/", response_model=List[Dict[str, Any]])
async def get_projects(user: User = Depends(get_current_user)):
    return await ProjectService.get_all_projects(user.id)

@router.post("/", response_model=Dict[str, Any])
async def create_project(req: CreateProjectRequest, user: User = Depends(get_current_user)):
    return await ProjectService.create_project(
        name=req.name,
        language=req.language,
        repo_url=req.repo_url,
        user_id=user.id
    )

@router.post("/{project_id}/scan", response_model=Dict[str, Any])
async def start_scan(project_id: int, user: User = Depends(get_current_user)):
    return await ScannerService.trigger_scan(project_id, user.id)
