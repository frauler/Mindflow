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

router = APIRouter(prefix="/articles", tags=["articles"])

@router.post("/", response_model=ArticlePublic, status_code=status.HTTP_200_OK)
async def create_article(session: SessionDep, article_in: ArticleCreate, user: CurrentUser):
    article_repository = ArticlesRepository(session)
    article_in.author_id = user.id
    article_create = await article_repository.create_article(article_in)

    return ArticlePublic(**article_create.__dict__)


@router.get("/{id}", response_model=ArticlePublic, status_code=status.HTTP_200_OK)
async def get_article_by_id(
        session: SessionDep,
        id: int,
        current_user: CurrentUser
    ):
    article_repository = ArticlesRepository(session)
    article = await article_repository.get_article_by_id(id)
    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Запрашиваемая статья не найдена"
        )
    
    if article.status != ArticleStatus.published:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Пользователь не имеет прав для выполнения действия"
            )

    return ArticlePublic(**article.__dict__)


@router.get(
            "/",
            response_model=ArticlesPublic,
            status_code=status.HTTP_200_OK
        )
async def get_articles(
        session: SessionDep, 
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
    articles = await article_repository.get_all_articles(limit=limit, offset=offset, status=status)

    return ArticlesPublic(data=articles)


@router.patch("/{id}", response_model=ArticlePublic, status_code=status.HTTP_200_OK)
async def update_article_me(
        session: SessionDep,
        article_in: ArticleUpdate,
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
    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Пользователь не имеет прав для выполнения действия"
        )
    update_data = article_in.model_dump(exclude_unset=True)
    article_updated = await article_repository.update_article_by_id(id, update_data)

    return ArticlePublic(**article_updated.__dict__)


@router.delete("/{id}", response_model=ArticlePublic, status_code=status.HTTP_200_OK)
async def delete_article_me(
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

    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Пользователь не имеет прав для выполнения действия"
        )
    article_deleted= await article_repository.delete_article(id)

    return ArticlePublic(**article_deleted.__dict__)