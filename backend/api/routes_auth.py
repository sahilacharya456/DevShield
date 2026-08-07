from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.orm import User, Organization
from backend.security.auth import verify_password, get_password_hash, create_access_token, get_current_user
from backend.config import settings
from backend.security.rate_limiter import limiter
from fastapi import Request

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    organization_id: int | None = None

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change current user's password"""
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password updated successfully"}

@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Streamlined FYP Demo: Reset password directly without email validation"""
    result = await db.execute(select(User).filter(User.email == payload.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
        
    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user)
    await db.commit()
    return {"message": "Password reset successfully"}

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests"""
    result = await db.execute(select(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check existing user
    result = await db.execute(select(User).filter((User.username == user_in.username) | (User.email == user_in.email)))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this username or email already exists in the system.",
        )
    
    # Check if first user -> make Admin (use COUNT not full table load)
    count_res = await db.execute(select(func.count(User.id)))
    is_first = count_res.scalar() == 0
    role = "Admin" if is_first else "Developer"

    # Provision an Organization for the new user
    org_name = f"{user_in.username}'s Org"
    org = Organization(name=org_name)
    db.add(org)
    await db.flush() # Flush to get org.id

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=role,
        organization_id=org.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
