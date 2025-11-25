from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.repository.users import UserRepository
from app.api.deps import (
    get_current_active_admin,
    SessionDep,
    CurrentUser
)
from app.schemas.users import (
    UserCreate,
    UserRegister,
    UserPublic,
    UsersPublic
)

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/", 
    dependencies=[Depends(get_current_active_admin)],
    response_model=UserPublic,
    status_code=status.HTTP_200_OK
)
async def create_user(session: SessionDep, user_in: UserRegister) -> Any:
    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_login(user_in.login)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует",
        )
    user_create = UserRegister.model_validate(user_in)
    user = await user_repository.create_user(user_create)
    
    return UserPublic(**user.__dict__)

@router.get(
    "/{login}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK
)
async def read_user(session: SessionDep, login: str) -> Any:
    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_login(login)
    if user is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    
    return UserPublic(**user.__dict__)

@router.get(
    "/",
    response_model=UsersPublic,
    status_code=status.HTTP_200_OK
)
async def read_all_users(session: SessionDep) -> Any:
    user_repository = UserRepository(session)
    all_users = await user_repository.get_all_users()

    return UsersPublic(data=all_users)
