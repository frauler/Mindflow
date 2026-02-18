from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.articles import ArticlesRepository
from app.repository.users import UserRepository
from app.api.deps import (
    get_current_active_admin,
    SessionDep,
    CurrentUser
)
from app.core.database import get_db
from app.core.config import settings
from app.schemas.articles import (
    ArticleCreate,
    ArticleUpdate,
    ArticlePublic,
    ArticlesPublic,
    ArticleStatusUpdate,
    ArticleViewsUpdate,
    ArticleVotesUpdate,
    ArticleStatus
)


router = APIRouter(prefix="/admin", tags=["admin"])


@router.patch(
            "/articles/{id}",
            response_model=ArticlePublic,
            dependencies=[Depends(get_current_active_admin)],
            status_code=status.HTTP_200_OK
        )
async def update_article(
        session: SessionDep,
        article_in: ArticleUpdate,
        id: int
    ):
    article_repository = ArticlesRepository(session)
    article = await article_repository.get_article_by_id(id)

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Запрашиваемая статья не найдена"
        )
    update_data = article_in.model_dump(exclude_unset=True)
    article_updated = await article_repository.update_article_by_id(id, update_data)

    return ArticlePublic(**article_updated.__dict__)


@router.patch(
        "/articles/{id}/status-change",
        response_model=ArticlePublic,
        dependencies=[Depends(get_current_active_admin)],
        status_code=status.HTTP_200_OK
    )
async def update_article_status(
        session: SessionDep,
        id: int,
        status: str = ArticleStatus.published
    ):
    article_repository = ArticlesRepository(session)
    article = await article_repository.get_article_by_id(id)

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Запрашиваемая статья не найдена"
        )
    
    if status not in ArticleStatus:
        raise HTTPException(
            status_code=406,
            detail="Переданы неверные параметры"
        )

    article_updated = await article_repository.update_status(id, status)

    return ArticlePublic(**article_updated.__dict__)


@router.delete(
        "/articles/{id}",
        response_model=ArticlePublic,
        dependencies=[Depends(get_current_active_admin)],
        status_code=status.HTTP_200_OK
    )
async def delete_article(
        session: SessionDep,
        current_user: CurrentUser,
        id: int
    ):
    article_repository = ArticlesRepository(session)
    article = await article_repository.get_article_by_id(id)

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Запрашиваемая статья не найдена"
        )

    article_deleted= await article_repository.delete_article(id)

    return ArticlePublic(**article_deleted.__dict__)