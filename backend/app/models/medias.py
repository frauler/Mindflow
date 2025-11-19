from __future__ import annotations
from datetime import datetime
from sqlalchemy import func, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

class MediaModel(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger(), nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    article: Mapped["ArticleModel"] = relationship(back_populates="medias")

from app.models.articles import ArticleModel