from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.users import UserRepository
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.schemas.users import (
    UserCreate,
    UserRegister,
    UserUpdate,
    UserPasswordUpdate,
    UserPublic,
    UsersPublic
)

router = APIRouter(tags=["auth"])

@router.post("/signup", response_model=UserPublic)
async def create_user(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    user = await user_repository.get_user_by_login(user_in.login)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует",
        )
    user_create = UserRegister.model_validate(user_in)
    user = await user_repository.create_user(user_create)
    return user