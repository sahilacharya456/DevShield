from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.engine.sandbox.phantom_executor import PhantomScanEngine
from backend.security.auth import get_pro_user

router = APIRouter()
engine = PhantomScanEngine()

class PhantomscanRequest(BaseModel):
    target: str
    options: dict = {}

@router.post("/run")
async def run_module(req: PhantomscanRequest, user=Depends(get_pro_user)):
    return await engine.run(req.model_dump())
