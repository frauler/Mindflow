from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.votes import VoteModel
from app.schemas.votes import VoteCreate, VotePublic, VotesPublic
from app.repository.articles import ArticlesRepository

class VotesRepository:
    """Репозиторий для работы с голосами пользователей."""

    def __init__(self, db: AsyncSession):
        """Инициализация репозитория.

        db: Асинхронная сессия базы данных.
        """
        self.db = db
        self.model = VoteModel

    # ---------------- CREATE ----------------
    async def add_vote(self, vote: VoteCreate) -> VotePublic:
        """Добавляет голос пользователя к статье и возвращает объект голоса.

        vote: Схема с данными для нового голоса.
        """
        obj = self.model(**vote.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

        # Обновляем количество голосов на статье
        article_repo = ArticlesRepository(self.db)
        await article_repo.change_votes_score(vote.article_id, 1)

        return VotePublic.model_validate(obj)
    
    # ---------------- READ ----------------
    async def get_vote_by_user_and_article(self, user_id, article_id) -> VotePublic | None:
        """Возвращает голос пользователя для конкретной статьи, если он существует.

        user_id: ID пользователя.
        article_id: ID статьи.
        """
        result = await self.db.execute(
            select(self.model).where(
                (self.model.user_id == user_id) &
                (self.model.article_id == article_id)
            )
        )
        vote_obj = result.scalars().first()
        return VotePublic.model_validate(vote_obj) if vote_obj else None

    async def get_all_votes(self) -> VotesPublic:
        """Возвращает все голоса в базе."""
        result = await self.db.execute(select(self.model))
        votes = result.scalars().all()
        return VotesPublic.model_validate({"data": votes})

    # ---------------- DELETE ----------------
    async def remove_vote(self, article_id, user_id) -> VotePublic | None:
        """Удаляет голос пользователя для конкретной статьи и обновляет счетчик голосов.

        article_id: ID статьи.
        user_id: ID пользователя.
        """
        vote = await self.get_vote_by_user_and_article(user_id, article_id)
        if vote is None:
            return None

        await self.db.execute(
            delete(self.model).where(self.model.id == vote.id)
        )
        await self.db.commit()

        # Уменьшаем количество голосов на статье
        article_repo = ArticlesRepository(self.db)
        await article_repo.change_votes_score(article_id, -1)

        return vote
