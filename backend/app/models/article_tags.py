from __future__ import annotations
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

class ArticleTagModel(Base):
    __tablename__ = "article_tags"

    __table_args__ = (
        UniqueConstraint("article_id", "tag_id", name="uix_article_tags_article_tag"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False)

    article: Mapped["ArticleModel"] = relationship(back_populates="article_tags")
    tag: Mapped["TagModel"] = relationship(back_populates="article_tags")

from app.models.articles import ArticleModel
from app.models.tags import TagModel