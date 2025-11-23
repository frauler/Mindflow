from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    Модель для добавления пользователя в базу данных
    """
    username: str = Field(..., description="Имя пользователя")
    login: str = Field(..., description="Логин пользователя")
    hashed_password: str = Field(..., description="Хэш-пароль пользователя")
    is_admin: bool = False


class UserRegister(BaseModel):
    """
    Модель для регистрации пользователя
    Используется для передачи параметров через API
    """
    username: str
    login: str
    password: str


class UserUpdate(BaseModel):
    """
    Модель для обновления данных пользователя
    """
    username: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    """
    Модель для обновления пароля пользователя
    Используется для передачи параметров через API
    """
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    """
    Модель для выдачи данных о пользователе
    """
    id: int
    login: str
    username: str
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
