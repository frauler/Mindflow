from __future__ import annotations
from datetime import datetime
from sqlalchemy import func, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from typing import List

class TagModel(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    article_tags: Mapped[List["ArticleTagModel"]] = relationship(back_populates="tag")

from app.models.article_tags import ArticleTagModel