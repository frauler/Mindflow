from __future__ import annotations
import enum
from datetime import datetime
from sqlalchemy import func, Enum, Integer, String, Text, ForeignKey, BigInteger, DateTime, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from typing import List

class ArticleStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class ArticleModel(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus, name="article_status_enum"),
        nullable=False,
        server_default=text(f"'{ArticleStatus.draft.value}'")
    )
    views_count: Mapped[int] = mapped_column(BigInteger(), server_default="0", nullable=False)
    votes_score: Mapped[int] = mapped_column(Integer(), server_default="0", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["UserModel"] = relationship(back_populates="articles")
    votes: Mapped[List["VoteModel"]] = relationship(back_populates="article")
    article_tags: Mapped[List["ArticleTagModel"]] = relationship(back_populates="article")
    medias: Mapped[List["MediaModel"]] = relationship(back_populates="article")

from app.models.users import UserModel
from app.models.votes import VoteModel
from app.models.article_tags import ArticleTagModel
from app.models.medias import MediaModel