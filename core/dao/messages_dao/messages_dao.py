from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.database import async_session_maker
from core.dao.base import BaseDao
from core.models.messages_models import Messages
from core.models.image_models import Image
from core.models.users_models import Users


class MessagesDao(BaseDao):
    model = Messages

    @classmethod
    async def show_all_data(cls):
        async with async_session_maker() as session:
            """
            SELECT messages.message, messages.time_sent, images.image_path, users.name FROM messages
            LEFT JOIN users ON messages.user_id = users.id
            LEFT JOIN images ON messages.user_id = images.user_id
            ORDER BY messages.id
            LIMIT 50
            """

            try:
                query = (select(cls.model.message, cls.model.time_sent, Image.image_path, Users.name)
                         .select_from(cls.model)
                         .join(Users, cls.model.user_id == Users.id, isouter=True)
                         .join(Image, cls.model.user_id == Image.user_id, isouter=True)
                         .order_by(cls.model.id)
                         .limit(50))
                result = await session.execute(query)
                return result.mappings().all()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    print(f"Database exc show database: {str(e)}")
                else:
                    print(f"Unknown exc: {str(e)}")
