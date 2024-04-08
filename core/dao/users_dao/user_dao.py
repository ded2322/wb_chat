from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.database import async_session_maker
from core.dao.base import BaseDao
from core.models.users_models import Users
from core.models.image_models import Image


class UserDao(BaseDao):
    model = Users

    @classmethod
    async def found_name_by_id(cls, id_user):
        async with async_session_maker() as session:
            try:
                query = select(cls.model.name).filter_by(id=id_user)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")

    @classmethod
    async def found_id_by_name(cls, name):
        async with async_session_maker() as session:
            try:
                query = select(cls.model.id).filter_by(name=name)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")

    @classmethod
    async def select_user_info(cls, user_id):
        """
        SELECT users.name, users.password, images.image_path FROM users
        LEFT JOIN images on users.id = images.user_id
        """
        async with async_session_maker() as session:
            try:
                query = (select(cls.model.name, cls.model.password, Image.image_path)
                         .select_from(cls.model)
                         .join(Image, cls.model.id == Image.user_id, isouter=True)
                         .where(cls.model.id == user_id)
                         )
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")
