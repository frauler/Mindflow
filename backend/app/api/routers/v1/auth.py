import jwt
from jwt.exceptions import InvalidTokenError
from typing import Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from app.core import security
from app.repository.users import UserRepository
from app.api.deps import (
    SessionDep,
    CurrentUser,
    set_access_token_cookie,
    set_refresh_token_cookie, 
    get_refresh_cookie_requierd
)
from app.repository.users import UserRepository
from app.core.config import settings
from app.models.users import UserModel
from app.schemas.users import (
    UserRegister,
    UserPublic,
    Token,
    TokenPayload,
    UserWithToken
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserWithToken, status_code=status.HTTP_200_OK)
async def register_user(session: SessionDep, response: Response, user_in: UserRegister) -> Any:
    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_login(user_in.login)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином или уже существует",
        )
    user = await user_repository.create_user(user_in)

    access_token  = await set_access_token_cookie(response=response, user=user)
    refresh_token  = await set_refresh_token_cookie(response=response, user=user)

    return UserWithToken(**user.__dict__, access_token=access_token, refresh_token=refresh_token)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(session: SessionDep, response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user_repository = UserRepository(session)
    user = await user_repository.authentificate(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    
    access_token = await set_access_token_cookie(response=response, user=user)
    refresh_token = await set_refresh_token_cookie(response=response, user=user)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login-test", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"info": "Вы вышли из аккаунта"}


@router.post("/refresh", response_model=Token)
async def refresh_token(session: SessionDep, response: Response, refresh_token: str = Depends(get_refresh_cookie_requierd)):
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не удалось проверить учетные данные",
        )
    user = await session.get(UserModel, int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Обновляем access и refresh token
    access_token = await set_access_token_cookie(response=response, user=user)
    refresh_token = await set_refresh_token_cookie(response=response, user=user)

    # Возвращаем access token в JSON для фронтенда
    return Token(access_token=access_token, refresh_token=refresh_token)