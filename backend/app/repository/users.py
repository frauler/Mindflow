from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import UserModel
from app.schemas.users import (
    UserCreate,
    UserRegister,
    UserPublic,
    UsersPublic,
    UserUpdate
)
from app.core.security import get_password_hash, verify_password


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: AsyncSession):
        """Инициализация репозитория.

        Args:
            db: Асинхронная сессия базы данных.
        """
        self.db = db
        self.model = UserModel

    # ---------------- CREATE ----------------
    async def create_user(self, user: UserRegister) -> UserPublic:
        """Создание нового пользователя.

        Args:
            user: Данные пользователя для регистрации.

        Returns:
            UserPublic: Представление созданного пользователя.
        """
        user_create = UserCreate.model_validate({
            "username": user.username,
            "login": user.login,
            "hashed_password": get_password_hash(user.password),
            "is_admin": False,
        })
        obj = self.model(**user_create.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return UserPublic.model_validate(obj)

    # ---------------- READ ----------------
    async def get_user_by_id(self, user_id: int) -> UserPublic | None:
        """Получение пользователя по ID.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            UserPublic | None: Найденный пользователь или None, если запись не найдена.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == user_id)
        )
        obj = result.scalars().first()
        return UserPublic.model_validate(obj) if obj else None

    async def get_user_by_login(self, search_login: str) -> UserPublic | None:
        """Получение пользователя по логину.

        Args:
            search_login: Логин пользователя.

        Returns:
            UserPublic | None: Найденный пользователь или None, если запись не найдена.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.login == search_login)
        )
        obj = result.scalars().first()
        return UserPublic.model_validate(obj) if obj else None

    async def get_all_users(self) -> UsersPublic:
        """Получение списка всех пользователей.

        Returns:
            UsersPublic: Обёртка с массивом пользователей.
        """
        result = await self.db.execute(select(self.model))
        users = result.scalars().all()
        return UsersPublic.model_validate({"data": users})
    
    async def authentificate(self, login, password) -> UserPublic | None:
        db_user = await self.db.execute(
            select(self.model).where(self.model.login == login)
        )
        obj = db_user.scalars().first()
        if not obj:
            return None
        if not verify_password(password, obj.hashed_password):
            return None
        return UserPublic.model_validate(obj)

    # ---------------- UPDATE ----------------
    async def update_user_by_id(self, user_id: int, new_data: UserUpdate) -> UserPublic | None:
        """Обновление данных пользователя по ID.

        Args:
            user_id: Идентификатор пользователя.
            new_data: Новые данные пользователя.

        Returns:
            UserPublic | None: Обновлённый пользователь или None, если запись не найдена.
        """
        await self.db.execute(
            update(self.model)
            .where(self.model.id == user_id)
            .values(**new_data.model_dump())
        )
        await self.db.commit()
        return await self.get_user_by_id(user_id)

    # ---------------- DELETE ----------------
    async def delete_user_by_id(self, user_id: int) -> UserPublic | None:
        """Удаление пользователя по ID.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            UserPublic | None: Удалённый пользователь или None, если запись не найдена.
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            return None

        await self.db.execute(
            delete(self.model)
            .where(self.model.id == user_id)
        )
        await self.db.commit()
        return user
