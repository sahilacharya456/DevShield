from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from backend.models.database import get_db
from backend.security.auth import get_current_admin
from backend.models.orm import User

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

class RoleUpdateRequest(BaseModel):
    role: str

@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """List all users (Admin only)"""
    result = await db.execute(select(User).order_by(User.id.desc()))
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=str(u.created_at)
        )
        for u in users
    ]

@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    payload: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Promote or demote a user (Admin only)"""
    if payload.role not in ["Admin", "Developer"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'Admin' or 'Developer'.")
        
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    # Prevent admin from demoting themselves
    if user.id == current_user.id and payload.role != "Admin":
        raise HTTPException(status_code=400, detail="Cannot demote yourself.")
        
    user.role = payload.role
    db.add(user)
    await db.commit()
    
    return {"message": f"User {user.username} role updated to {payload.role}"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a user (Admin only)"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account.")
        
    await db.delete(user)
    await db.commit()
    
    return {"message": f"User {user.username} permanently deleted."}
