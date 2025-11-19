from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

class BaseDAO:
    """
    Класс для работы с CRUD запросами к базе данных
    """
    async def create(self, db: AsyncSession, data):
        """
        Создаёт запись в таблице

        :param db: Асинхронная сессия БД
        :param data: Заполненная модель таблицы БД
        """
        db.add(data)
        await db.commit()
        await db.refresh(data)
        return data
    
    async def read(self, db: AsyncSession, table_model, field_name: str, value):
        """
        Чтение записи из таблицы

        :param db: Асинхронная сессия БД
        :param table_model: Модель таблицы БД
        :param field_name: Имя поля для поиска
        :param value: Значение для поиска
        :return: Найденная запись или None, если запись не найдена
        """
        # Выстаскиваем атрибут из модели таблицы  по имени
        # Должно получиться (table_model.field_name)
        field = getattr(table_model, field_name)
        result = await db.execute(
            select(table_model).where(field == value)
        )
        return result.scalars().first()

    async def read_all(db: AsyncSession, table_model):
        """
        Чтение всех записей из таблицы

        :param db: Асинхронная сессия БД
        :param table_model: Модель таблицы БД
        :return: Все найденные записи
        """
        result = await db.execute(
            select(table_model)
        )
        return result.scalars().all()
    
    async def update(self, db: AsyncSession, table_model, field_name: str, value, new_data):
        """
        Обновление записи из таблицы с заданным полем

        Если задать что-то, кроме id - будет обновлено только первое поле, содержащее значение
        :param db: Асинхронная сессия БД
        :param table_model: Модель таблицы БД
        :param field_name: Имя поля для поиска
        :param value: Значение для поиска
        :return: Обновлённая запись или None, если запись не найдена
        """  
        existing_row = self.read(db, table_model, field_name, value)
        if existing_row is None:
            return None
        field = getattr(table_model, field_name)
        await db.execute(
            update(table_model).where(field == value).values(**new_data.model_dump())
        )
        await db.commit()
        return self.read(db, table_model, field_name, value)
    
    async def delete(self, db: AsyncSession, table_model, field_name: str, value):
        """
        Удаление записей из таблицы с заданным полем

        Если задать что-то, кроме id - будет удалено только первое поле, содержащее значение
        :param db: Асинхронная сессия БД
        :param table_model: Модель таблицы БД
        :param field_name: Имя поля для поиска
        :param value: Значение для поиска
        :return: Удалённая запись или None, если запись не найдена
        """ 
        existing_row = self.read(db, table_model, field_name, value)
        if existing_row is None:
            return None
        field = getattr(table_model, field_name)
        await db.execute(delete(table_model).where(field == value))
        await db.commit()
        return existing_row