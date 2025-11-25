from __future__ import annotations
from datetime import datetime
from sqlalchemy import func, Boolean, String, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from typing import List

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    real_name: Mapped[str] = mapped_column(String(25), unique=False, nullable=True)
    login: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    votes: Mapped[List["VoteModel"]] = relationship(back_populates="user")
    articles: Mapped[List["ArticleModel"]] = relationship(back_populates="user")

from app.models.articles import ArticleModel
from app.models.votes import VoteModel