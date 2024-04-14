from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError

from core.database import async_session_maker
from core.dao.base import BaseDao
from core.models.messages_models import Messages
from core.models.image_models import Image
from core.models.users_models import Users
from core.logs.logs import logger_error


class MessagesDao(BaseDao):
    model = Messages

    @classmethod
    async def show_all_data(cls):
        """
        Возвращает последние 50 сообщений пользователей. Вместе с их аватарками
        """
        async with async_session_maker() as session:
            """
            SELECT messages.message, messages.time_sent, images.image_path, users.name FROM messages
            LEFT JOIN users ON messages.user_id = users.id
            LEFT JOIN images ON messages.user_id = images.user_id
            ORDER BY messages.id
            LIMIT 50
            """
            try:
                query = (select(cls.model.id.label("message_id"), cls.model.message, cls.model.time_send,
                                Image.image_path,
                                Users.id.label("user_id"), Users.name)
                         .select_from(cls.model)
                         .join(Users, cls.model.user_id == Users.id, isouter=True)
                         .join(Image, cls.model.user_id == Image.user_id, isouter=True)
                         .order_by(desc(cls.model.id))
                         .limit(50))
                result = await session.execute(query)
                return result.mappings().all()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in show_all_data: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in show_all_data: {str(e)}")

    @classmethod
    async def load_messages(cls, message_id: int):
        """

        :param message_id:
        :return:
        """
        async with async_session_maker() as session:
            """
            SELECT messages.id, messages.message, messages.time_send, images.image_path, users.name FROM messages
            LEFT JOIN users ON messages.user_id = users.id
            LEFT JOIN images ON messages.user_id = images.user_id
            WHERE messages.id < message_id
            ORDER BY id DESC
            LIMIT 50;
            """
            try:
                query = (select(cls.model.id, cls.model.message, cls.model.time_send, Image.image_path, Users.name)
                         .select_from(cls.model)
                         .join(Users, cls.model.user_id == Users.id, isouter=True)
                         .join(Image, cls.model.user_id == Image.user_id, isouter=True)
                         .where(cls.model.id < message_id)
                         .order_by(desc(cls.model.id))
                         .limit(50))
                result = await session.execute(query)
                return result.mappings().all()

            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in load_messages: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in load_messages: {str(e)}")
