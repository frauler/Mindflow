from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.users import UserRepository
from app.core.database import get_db
from app.core.config import settings
from app.schemas.articles import (
    ArticleCreate,
    ArticleUpdate,
    ArticlePublic,
    ArticlesPublic,
    ArticleStatusUpdate,
    ArticleViewsUpdate,
    ArticleVotesUpdate
)

router = APIRouter(prefix="/articles", tags=["articles"])

@router.post("/", response_model=ArticlePublic)
async def create_article(token: str, article: ArticleCreate, db: AsyncSession = Depends(get_db)):
    pass
