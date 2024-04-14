from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.dao.base import BaseDao
from core.database import async_session_maker
from core.models.image_models import Image


class ImageDao(BaseDao):
    model = Image
