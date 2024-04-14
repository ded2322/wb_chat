import asyncio
from pathlib import Path
from PIL import Image

from core.tasks.celery_config import celery
from core.dao.image_dao.image_dao import ImageDao
from core.logs.logs import logger_error


@celery.task
def process_pic(
        path: str,
        user_id: int
):
    """
    Уменьшает изображение с сохранением пропорций и высоким качеством
    """
    try:
        img_path = Path(path)
        img = Image.open(img_path)

        max_size = (72, 72)
        # Уменьшение изображение с учетом его сторон
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        image_path = f"core/static/resize_images/resize_image_user_{user_id}.webp"
        img.save(image_path)

        # Создание цикла событий
        loop = asyncio.get_event_loop()
        user_id = loop.run_until_complete(ImageDao.found_data_by_column("id", user_id=user_id))
        loop.run_until_complete(ImageDao.update_data(user_id["id"], image_path=image_path))
    except Exception as e:
        logger_error.error(f"Error in process_pic {str(e)}")
