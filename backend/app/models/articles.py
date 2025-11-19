from __future__ import annotations
from datetime import datetime
from sqlalchemy import func, Integer, Boolean, String, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from typing import List

class ArticleModel(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    views_conut: Mapped[int] = mapped_column(BigInteger(), server_default=0, nullable=False)
    votes_score: Mapped[int] = mapped_column(Integer(), server_default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=datetime.now)
    published_at: Mapped[datetime] = mapped_column()

    user: Mapped["UserModel"] = relationship(back_populates="articles")
    votes: Mapped[List["VoteModel"]] = relationship(back_populates="articles")
    article_tags: Mapped[List["ArticleTagModel"]] = relationship(back_populates="articles")
    medias: Mapped[List["MediasModel"]] = relationship(back_populates="articles")

from app.models.users import UserModel
from app.models.votes import VoteModel
from app.models.article_tags import ArticleTagModel
from app.models.medias import MediasModel