from fastapi import APIRouter, Depends
from backend.security.auth import get_current_user, Depends
from pydantic import BaseModel
from backend.engine.deobfuscator.neural_deobfuscator import MalwareForgeEngine

router = APIRouter()
engine = MalwareForgeEngine()

class MalwareforgeRequest(BaseModel):
    target: str
    options: dict = {}

@router.post("/run")
async def run_module(req: MalwareforgeRequest, user=Depends(get_current_user)):
    return await engine.run(req.model_dump())
