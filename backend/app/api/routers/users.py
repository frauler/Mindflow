from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.repository.users import Userrepository

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

router = APIRouter(prefix="/users", tags=["users"])

