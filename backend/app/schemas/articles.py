from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.articles import ArticleStatus


class ArticleCreate(BaseModel):
    """
    Модель для добавления статьи в базу данных
    """
    author_id: int = Field(..., description="ID автора статьи")
    title: str = Field(..., description="Заголовок статьи")
    summary: str = Field(..., description="Краткое предисловие статьи")
    body: str = Field(..., description="Основной текст с содержанием статьи")
    status: ArticleStatus = Field(ArticleStatus.draft, description="Статус статьи")


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    body: Optional[str] = None


class ArticleStatusUpdate(BaseModel):
    status: ArticleStatus = Field(..., description="Новый статус")
    published_at: datetime = None


class ArticleViewsUpdate(BaseModel):
    views_count: int = Field(..., ge=0, description="Количество просмотров (>=0)")


class ArticleVotesUpdate(BaseModel):
    votes_score: int = Field(..., ge=0, description="Количество голосов (>=0)")


class ArticlePublic(BaseModel):
    id: int
    author_id: int
    title: str
    summary: str
    body: str
    status: ArticleStatus
    views_count: int
    votes_score: int

    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticlesPublic(BaseModel):
    data: list[ArticlePublic]
    model_config = {"from_attributes": True}