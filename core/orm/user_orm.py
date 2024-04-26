from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.orm.base_orm import BaseOrm
from core.database import async_session_maker
from core.logs.logs import logger_error
from core.models.image_models import Image
from core.models.users_models import Users


class UserOrm(BaseOrm):
    model = Users

    @classmethod
    async def user_info(cls, user_id):
        """
        Находит всю информацию по пользователю
        Возвращает все данные по пользователю
        """
        async with async_session_maker() as session:
            try:
                """
                SELECT users.name, users.password, images.image_path FROM users
                LEFT JOIN images on users.id = images.user_id
                """
                query = (
                    select(
                        cls.model.id.label("user_id"),
                        cls.model.name,
                        cls.model.role,
                        Image.image_path.label("user_avatar"),
                    )
                    .select_from(cls.model)
                    .join(Image, cls.model.id == Image.user_id, isouter=True)
                    .where(cls.model.id == user_id)
                )
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in select_user_info: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in select_user_info: {str(e)}")

    @classmethod
    async def select_role_name_user(cls, **kwargs):
        async with async_session_maker() as session:
            try:
                """
                SELECT role, name FROM users
                WHERE **kwargs
                """
                query = select(cls.model.role, cls.model.name).filter_by(**kwargs)
                result = await session.execute(query)

                return result.mappings().one_or_none()
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    logger_error.error(f"SQLAlchemy exc in select_user_info: {str(e)}")
                else:
                    logger_error.error(f"Unknown exc in select_user_info: {str(e)}")
