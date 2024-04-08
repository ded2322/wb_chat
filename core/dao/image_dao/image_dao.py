from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.dao.base import BaseDao
from core.database import async_session_maker
from core.models.image_models import Image


class ImageDao(BaseDao):
    model = Image
    @classmethod
    async def found_id_by_userid(cls, user_id):
        async with async_session_maker() as session:
            try:
                query = select(cls.model.id).filter_by(user_id=user_id)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")

    @classmethod
    async def file_path(cls, user_id):
        async with async_session_maker() as session:
            try:
                query = select(cls.model.image_path).filter_by(user_id=user_id)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")