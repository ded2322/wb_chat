from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from core.database import async_session_maker
from core.logs.logs import logger_error


class BaseOrm:
    model = None

    @classmethod
    async def show_all_data(cls):
        """
        Выборка всех данных из таблицы, отдает в виде списка словарей
        """
        async with async_session_maker() as session:
            try:
                """
                SELECT * FROM csl.model;
                """
                query = select(cls.model.__table__.columns)
                result = await session.execute(query)
                return result.mappings().all()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in show database: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in show database: {str(e)}")

    @classmethod
    async def found_one_or_none(cls, **kwargs):
        """
        Находит строку в таблице, отдает в виде словаря
        """
        async with async_session_maker() as session:
            """
            SELECT * FROM csl.model
            WHERE **kwargs;
            """
            try:
                query = select(cls.model.__table__.columns).filter_by(**kwargs)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in found or none: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in found or none: {str(e)}")

    @classmethod
    async def found_data_by_column(cls, column, **kwargs):
        """
        Находит имя пользователя по его id
        Возвращает только имя
        """
        async with async_session_maker() as session:
            """
            SELECT column FROM csl.model
            WHERE **kwargs;
            """

            try:
                column = getattr(cls.model, column)
                query = select(column).filter_by(**kwargs)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in found_data_by_id: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc un found_data_by_id: {str(e)}")

    @classmethod
    async def insert_data(cls, **kwargs):
        """
        Добавляет данные в таблицу
        """
        async with async_session_maker() as session:
            """
            INSERT INTO csl.model VALUES
            (**kwargs);
            """
            try:
                query = insert(cls.model).values(**kwargs)
                await session.execute(query)
                await session.commit()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in insert_data: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in insert_data: {str(e)}")

    @classmethod
    async def update_data(cls, id: int, **kwargs):
        """
        Обновляет данные в таблице.
        Принимает id строки которую нужно обновить,
        столбец который нужно обновить
        новые данные которые нужно вставить в этот столбец
        """
        async with async_session_maker() as session:
            try:
                """
                UPDATE csl.model
                SET column = new_data;
                """
                query = update(cls.model).where(cls.model.id == id).values(**kwargs)
                await session.execute(query)
                await session.commit()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in update_data: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in update_data: {str(e)}")

    @classmethod
    async def delete_data(cls, **kwargs):
        """
        Удаляет данные из таблицы
        """
        async with async_session_maker() as session:
            """
            DELETE FROM csl.model
            WHERE **kwargs
            """
            try:
                query = delete(cls.model).filter_by(**kwargs)
                await session.execute(query)
                await session.commit()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in delete_data: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in delete_data: {str(e)}")
