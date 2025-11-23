from __future__ import annotations
from datetime import datetime
from sqlalchemy import func, SmallInteger, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base


class VoteModel(Base):
    __tablename__ = "votes"

    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="uix_votes_user_article"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False)
    value: Mapped[int] = mapped_column(SmallInteger(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["UserModel"] = relationship(back_populates="votes")
    article: Mapped["ArticleModel"] = relationship(back_populates="votes")

from app.models.articles import ArticleModel
from app.models.users import UserModel