from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError

from core.orm.base_orm import BaseOrm
from core.database import async_session_maker
from core.logs.logs import logger_error
from core.models.image_models import Image
from core.models.messages_models import Messages
from core.models.users_models import Users


class MessagesOrm(BaseOrm):
    model = Messages

    @classmethod
    async def get_message(cls, load_previous=False, message_id=None):
        """
        Загружает 50 сообщений пользователей. Вместе с их аватарками
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
                query = (
                    select(
                        cls.model.id.label("message_id"),
                        cls.model.message,
                        cls.model.time_send,
                        Image.image_path.label("user_avatar"),
                        Users.id.label("user_id"),
                        Users.name,
                        Users.role,
                    )
                    .select_from(cls.model)
                    .join(Users, cls.model.user_id == Users.id, isouter=True)
                    .join(Image, cls.model.user_id == Image.user_id, isouter=True)
                    .order_by(desc(cls.model.id))
                    .limit(50)
                )
                if load_previous and message_id is not None:
                    query = query.where(cls.model.id < message_id)

                result = await session.execute(query)
                return result.mappings().all()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in get_message: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in get_message: {str(e)}")
