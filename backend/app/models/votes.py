from __future__ import annotations
from datetime import datetime
from sqlalchemy import func, Integer, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from typing import List

class VoteModel(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer(), )
    username: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    bio: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=datetime.now)

    votes: Mapped[List["VoteModel"]] = relationship(back_populates="user")
    articles: Mapped[List["ArticleModel"]] = relationship(back_populates="user")

from app.models.articles import ArticleModel
from app.models.votes import VoteModel