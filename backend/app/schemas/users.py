from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    Модель для добавления пользователя в базу данных
    """
    login: str = Field(..., description="Логин пользователя")
    hashed_password: str = Field(..., description="Хэш-пароль пользователя")
    is_admin: bool = False


class UserRegister(BaseModel):
    """
    Модель для регистрации пользователя
    Используется для передачи параметров через API
    """
    login: str
    password: str # = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """
    Модель для обновления данных пользователя
    """
    real_name: Optional[str] | None = Field(default=None, description="Реальное имя пользователя")
    bio: Optional[str] | None = Field(default=None, description="Описание пользователя")


class UserPasswordUpdate(BaseModel):
    """
    Модель для обновления пароля пользователя
    Используется для передачи параметров через API
    """
    current_password: str
    new_password: str # = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    """
    Модель для выдачи данных о пользователе
    """
    id: int
    login: str
    real_name: Optional[str]
    bio: Optional[str]
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UsersPublic(BaseModel):
    """
    Модель для выдачи данных обо всех пользователях
    """
    data: list[UserPublic]

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserWithToken(UserPublic):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None