import shutil
from pathlib import Path

from fastapi import BackgroundTasks, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from core.chat.users.auth import decode_jwt_user_id
from core.dao.image_dao.image_dao import ImageDao
from core.logs.logs import logger_error


class ImageService:
    VALID_EXTENSIONS = ["png", "jpg", "webp"]

    @classmethod
    def is_valid_extension(cls, file_name: UploadFile) -> bool:
        """
        Проверка расширения файла
        :return: Если расширение доступно возвращает True
        """
        return file_name.filename.split(".")[-1] in cls.VALID_EXTENSIONS

    @classmethod
    async def save_resize_image(
        cls, token: str, image: UploadFile, background_tasks: BackgroundTasks
    ):
        """
        Принимает изображение, сохраняет изображение и уменьшает его размер.
        Возвращает сообщение об успешном сохранении
        """

        if not cls.is_valid_extension(image):
            logger_error.error(f"User try upload {str(image)}")
            return JSONResponse(
                status_code=400, content={"detail": "Invalid extension"}
            )

        user_id = int(decode_jwt_user_id(token))
        file_path_original = f"/core/static/original_images/original_{user_id}.webp"

        with open(file_path_original, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)

        image_path_resize = (
            f"/core/static/resize_images/resize_image_user_{user_id}.webp"
        )

        # image_path = cls.resize_image(file_path, user_id)
        # await cls.update_data(user_id, image_path)
        # выполняется в фоновом режиме
        background_tasks.add_task(
            cls.resize_image, file_path_original, image_path_resize
        )
        background_tasks.add_task(cls.update_file_path_user, user_id, image_path_resize)

    @staticmethod
    def resize_image(file_path: str, image_path_resize: str):
        """
        Уменьшает размер изображения
        """
        image = Path(file_path)
        img = Image.open(image)

        max_size = (72, 72)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        with open(image_path_resize, "wb") as file:
            img.save(file, format="WebP", lossless=True, quality=100, method=6)

    @classmethod
    async def update_file_path_user(cls, user_id, image_path):
        await ImageDao.update_data(user_id, image_path=image_path[5:])
