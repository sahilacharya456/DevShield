from fastapi import APIRouter, Depends
from backend.security.auth import get_current_user, Depends
from pydantic import BaseModel
from backend.engine.osint.attack_surface_mapper import OsintRadarEngine

router = APIRouter()
engine = OsintRadarEngine()

class OsintradarRequest(BaseModel):
    target: str
    options: dict = {}

@router.post("/run")
async def run_module(req: OsintradarRequest, user=Depends(get_current_user)):
    return await engine.run(req.model_dump())
