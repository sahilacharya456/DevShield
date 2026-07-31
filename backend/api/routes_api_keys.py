from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import secrets
import hashlib
from typing import List

from backend.models.database import get_db
from backend.models.orm import APIToken, User
from backend.security.auth import get_current_user

router = APIRouter()

class APITokenCreate(BaseModel):
    name: str

class APITokenResponse(BaseModel):
    id: int
    name: str
    token: str | None = None
    is_revoked: bool
    
    class Config:
        from_attributes = True

@router.post("/generate", response_model=APITokenResponse)
async def generate_token(
    req: APITokenCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User does not belong to an organization")
        
    raw_token = "devshield_" + secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    api_token = APIToken(
        organization_id=current_user.organization_id,
        name=req.name,
        token_hash=token_hash
    )
    db.add(api_token)
    await db.commit()
    await db.refresh(api_token)
    
    return {
        "id": api_token.id,
        "name": api_token.name,
        "token": raw_token,
        "is_revoked": api_token.is_revoked
    }

@router.get("/list", response_model=List[APITokenResponse])
async def list_tokens(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.organization_id:
        return []
        
    result = await db.execute(select(APIToken).filter(APIToken.organization_id == current_user.organization_id))
    tokens = result.scalars().all()
    
    return [
        {"id": t.id, "name": t.name, "is_revoked": t.is_revoked}
        for t in tokens
    ]

@router.delete("/revoke/{token_id}")
async def revoke_token(
    token_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(APIToken).filter(APIToken.id == token_id, APIToken.organization_id == current_user.organization_id))
    api_token = result.scalars().first()
    if not api_token:
        raise HTTPException(status_code=404, detail="Token not found")
        
    api_token.is_revoked = True
    await db.commit()
    return {"status": "success", "message": "Token revoked"}
