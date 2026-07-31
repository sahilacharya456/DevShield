from fastapi import APIRouter, Depends
from backend.learning.session_manager import SessionManager
from backend.security.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_history(limit: int = 10, user=Depends(get_current_user)):
    manager = SessionManager()
    history = await manager.get_history(user.id, limit)
    return {"history": history}
