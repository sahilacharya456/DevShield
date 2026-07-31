from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.engine.supplychain.chain_breaker import ChainBreakerEngine
from backend.security.auth import get_current_user

router = APIRouter()
engine = ChainBreakerEngine()

class ChainbreakerRequest(BaseModel):
    target: str = ""
    manifest_name: str | None = None
    manifest_content: str | None = None
    options: dict = {}

@router.post("/run")
async def run_module(req: ChainbreakerRequest, user=Depends(get_current_user)):
    return await engine.run(req.model_dump())
