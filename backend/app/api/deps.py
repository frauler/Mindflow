import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from datetime import timedelta
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.security import create_access_token
from app.core.database import get_db
from app.models.users import UserModel
from app.schemas.users import UserPublic, TokenPayload

# reusable_oauth2 = OAuth2PasswordBearer(
#     tokenUrl=f"{settings.API_V1_STR}/login"
# )


SessionDep = Annotated[AsyncSession, Depends(get_db)]

async def set_access_token_cookie(response: Response, user):
    access_token=create_access_token(
        user.id, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=False
    )
    return access_token

async def set_refresh_token_cookie(response: Response, user):
    refresh_token = create_access_token(
        user.id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="strict",
    )
    return refresh_token

async def get_access_cookie_requierd(request: Request):
    cookie_token = request.cookies.get('access_token')
    if not cookie_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не найден')
    return str(cookie_token)

async def get_refresh_cookie_requierd(request: Request):
    cookie_token = request.cookies.get('refresh_token')
    if not cookie_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не найден')
    return str(cookie_token)

TokenDep = Annotated[str, Depends(get_access_cookie_requierd)]

async def get_current_user(session: SessionDep, token: TokenDep) -> UserModel:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
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
    return user


CurrentUser = Annotated[UserPublic, Depends(get_current_user)]


async def get_current_active_admin(current_user: CurrentUser) -> UserModel:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Пользователь не имеет прав для выполнения действия"
        )
    return current_user