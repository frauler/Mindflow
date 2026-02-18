from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_password_hash, verify_password
from app.repository.users import UserRepository
from app.repository.articles import ArticlesRepository
from app.api.deps import (
    get_current_active_admin,
    SessionDep,
    CurrentUser
)
from app.schemas.users import (
    UserUpdate,
    UserPasswordUpdate,
    UserRegister,
    UserPublic,
    UsersPublic
)
from app.schemas.articles import (
    ArticlesPublic,
    ArticleStatus
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


@router.post("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    return UserPublic(**current_user.__dict__)


@router.patch(
        "/me",
        response_model=UserPublic,
        status_code=status.HTTP_200_OK
    )
async def update_user_me(session: SessionDep, user_in: UserUpdate, current_user: CurrentUser) -> Any:
    user_repository = UserRepository(session)
    update_data = user_in.model_dump(exclude_unset=True)
    user_updated = await user_repository.update_user_by_id(current_user.id, update_data)
    
    return UserPublic(**user_updated.__dict__)


@router.patch(
        "/me/password",
        response_model=UserPublic,
        status_code=status.HTTP_200_OK
    )
async def update_password_me(session: SessionDep, body: UserPasswordUpdate, current_user: CurrentUser) -> Any:
    user_repository = UserRepository(session)
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="Новый пароль не должен совпадать с старым"
        )
    hashed_password = get_password_hash(body.new_password)
    user_updated = await user_repository.update_user_password(current_user.id, hashed_password)
    
    return UserPublic(**user_updated.__dict__)


@router.get("/{login}/articles", response_model=ArticlesPublic, status_code=status.HTTP_200_OK)
async def get_user_articles(
        session: SessionDep,
        login: str,
        current_user: CurrentUser,
        status: str = ArticleStatus.published,
        limit: int = 10,
        offset: int = 0
    ):
    article_repository = ArticlesRepository(session)
    if status != ArticleStatus.published:
        if status not in ArticleStatus:
            raise HTTPException(
                status_code=406,
                detail="Переданы неверные параметры"
            )
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Пользователь не имеет прав для выполнения действия"
            )

    articles = await article_repository.get_all_articles(limit, offset, login, status)

    return ArticlesPublic(data=articles)