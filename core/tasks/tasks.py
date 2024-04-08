import asyncio
from pathlib import Path
from PIL import Image

from core.tasks.celery_config import celery
from core.dao.image_dao.image_dao import ImageDao


@celery.task
def process_pic(
        path: str,
        user_id: int
):
    """

    :param path:
    :param user_id:
    :return:
    """
    img_path = Path(path)
    img = Image.open(img_path)
    width = 72
    height = 72

    # Уменьшаем размер до 72x72 пикселей
    img_resized = img.resize((width, height))

    image_path = f"core/static/resize_images/resize_image_user_{user_id}.webp"
    # Сохраняем уменьшенное изображение
    img_resized.save(image_path)

    loop = asyncio.get_event_loop()
    user_id = loop.run_until_complete(ImageDao.found_id_by_userid(user_id))
    loop.run_until_complete(ImageDao.update_data(user_id["id"], "image_path", image_path))
