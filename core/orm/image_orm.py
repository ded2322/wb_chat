from core.orm.base_orm import BaseOrm
from core.models.image_models import Image


class ImageOrm(BaseOrm):
    model = Image
