from typing import Any
from datetime import datetime
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.users import UserRepository
from app.models.articles import ArticleModel, ArticleStatus
from app.schemas.articles import (
    ArticleCreate,
    ArticlePublic,
    ArticlesPublic,
    ArticleUpdate,
    ArticleStatusUpdate
)


class ArticlesRepository:
    """Репозиторий для работы со статьями"""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория.

        Args:
            db: Асинхронная сессия базы данных.
        """
        self.session = session
        self.model = ArticleModel


    # ---------------- CREATE ----------------
    async def create_article(self, article: ArticleCreate) -> ArticlePublic:
        """Создание новой статьи.

        Args:
            article: Данные статьи для создания.

        Returns:
            ArticlePublic: Представление созданной статьи.
        """
        obj = self.model(**article.model_dump())
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return ArticlePublic.model_validate(obj)


    # ---------------- READ ----------------
    async def get_article_by_id(self, article_id: int) -> ArticlePublic | None:
        """Получение статьи по ID.

        Args:
            article_id: Идентификатор статьи.

        Returns:
            ArticlePublic | None: Найденная статья или None, если запись не найдена.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == article_id)
        )
        obj = result.scalars().first()
        return ArticlePublic.model_validate(obj) if obj else None


    async def get_all_articles(
            self,
            limit: int,
            offset: int,
            login: str = None,
            status: str = ArticleStatus.published) -> list:
        """Получение списка статей по статусу.

        Returns:
            ArticlesPublic: Обёртка с массивом статей.
        """
        if login is None:
            q = (
                select(self.model)
                .where(
                    (self.model.status == status)
                )
                .order_by(ArticleModel.id.desc())
                .limit(limit)
                .offset(offset)
            )
        else:
            user_repository = UserRepository(self.session)
            user = await user_repository.get_user_by_login(login)
            q = (
                select(self.model)
                .where(
                    (self.model.status == status) & 
                    (self.model.author_id == user.id)
                )
                .order_by(ArticleModel.id.desc())
                .limit(limit)
                .offset(offset)
            )
        
        result = await self.session.execute(q)
        articles = result.scalars().all()
        return articles


    # ---------------- UPDATE ----------------
    async def update_article_by_id(self, article_id: int, new_data: dict) -> Any | None:
        """Обновление данных статьи по ID.

        Args:
            article_id: Идентификатор статьи.
            new_data: Новые данные статьи.

        Returns:
            ArticlePublic | None: Обновлённая статья или None, если запись не найдена.
        """
        await self.session.execute(
            update(self.model)
            .where(self.model.id == article_id)
            .values(**new_data)
        )
        await self.session.commit()
        return await self.get_article_by_id(article_id)
    

    async def update_status(self, article_id: int, new_status: str) -> ArticlePublic | None:
        """Обновление статуса статьи по ID.

        Args:
            article_id: Идентификатор статьи.
            new_status: Новые данные для статуса статьи.

        Returns:
            ArticlePublic | None: Обновлённая статья или None, если запись не найдена.
        """
        values = {"status": new_status}
        if new_status == ArticleStatus.published:
            values["published_at"] = datetime.now()

        ArticleStatusUpdate.model_validate(values)    

        await self.session.execute(
            update(self.model)
            .where(self.model.id == article_id)
            .values(**values)
        )
        await self.session.commit()
        return await self.get_article_by_id(article_id)


    async def increment_views(self, article_id: int, delta: int = 1) -> ArticlePublic | None:
        """Увеличение количества просмотров статьи.

        Args:
            article_id: Идентификатор статьи.
            delta: На сколько увеличить просмотры (по умолчанию 1).

        Returns:
            ArticlePublic | None: Обновлённая статья или None, если запись не найдена.
        """
        await self.session.execute(
            update(self.model)
            .where(self.model.id == article_id)
            .values(views_count=self.model.views_count + delta)
        )
        await self.session.commit()
        return await self.get_article_by_id(article_id)


    async def change_votes_score(self, article_id: int, delta: int) -> ArticlePublic | None:
        """Изменение количества голосов статьи.

        Args:
            article_id: Идентификатор статьи.
            delta: На сколько изменить количество голосов.

        Returns:
            ArticlePublic | None: Обновлённая статья или None, если запись не найдена.
        """
        await self.session.execute(
            update(self.model)
            .where(self.model.id == article_id)
            .values(votes_score=self.model.votes_score + delta)
        )
        await self.session.commit()
        return await self.get_article_by_id(article_id)


    # ---------------- DELETE ----------------
    async def delete_article(self, article_id: int) -> ArticlePublic | None:
        """Удаление статьи по ID.

        Args:
            article_id: Идентификатор статьи.

        Returns:
            ArticlePublic | None: Удалённая статья или None, если запись не найдена.
        """
        article = await self.get_article_by_id(article_id)
        if article is None:
            return None

        await self.session.execute(
            delete(self.model)
            .where(self.model.id == article_id)
        )
        await self.session.commit()
        return article
