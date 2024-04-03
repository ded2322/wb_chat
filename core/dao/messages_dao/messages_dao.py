from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.database import async_session_maker
from core.dao.base import BaseDao
from core.models.messages_models import Messages


class MessagesDao(BaseDao):
    model = Messages

    @classmethod
    async def show_all_data(cls):
        async with async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).order_by(cls.model.id.desc()).limit(50)
                result = await session.execute(query)
                return result.mappings().all()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")
