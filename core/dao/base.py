from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError
from core.database import async_session_maker


class BaseDao:
    model = None

    @classmethod
    async def show_all_data(cls):
        async with async_session_maker() as session:
            try:
                # query = select(cls.model.__table__.columns).order_by(cls.model.id.desc()).limit(50)
                query = select(cls.model.__table__.columns)
                result = await session.execute(query)
                return result.mappings().all()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")

    @classmethod
    async def found_or_none_data(cls, **kwargs):
        async with async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).filter_by(**kwargs)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc found or none : {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")

    @classmethod
    async def insert_data(cls, **kwargs):
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(**kwargs)
                await session.execute(query)
                await session.commit()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc found or none : {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")

    @classmethod
    async def update_data(cls, id: int, column, new_data):
        async with async_session_maker() as session:
            try:
                query = (update(cls.model).
                         where(cls.model.id == id).
                         values({column: new_data}))
                await session.execute(query)
                await session.commit()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc insert data: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")

    @classmethod
    async def delete_data(cls, **kwargs):
        async with async_session_maker() as session:
            try:
                query = delete(cls.model).filter_by(**kwargs)
                await session.execute(query)
                await session.commit()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc insert data: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")
