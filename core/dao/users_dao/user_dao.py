from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.database import async_session_maker
from core.dao.base import BaseDao
from core.models.users_models import Users


class UserDao(BaseDao):
    model = Users

    @classmethod
    async def found_name(cls, id_user):
        async with async_session_maker() as session:
            try:
                query = (select(cls.model.name)).filter_by(id=id_user)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")
