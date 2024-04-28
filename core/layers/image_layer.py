import shutil
import io
from pathlib import Path

from fastapi import BackgroundTasks, UploadFile
from PIL import Image
from starlette.responses import JSONResponse

from core.utils.auth import DecodeJWT
from core.orm.image_orm import ImageOrm
from core.logs.logs import logger_error


class ValidImage:
    VALID_EXTENSIONS = ["png", "jpg", "webp", "jpeg"]

    @classmethod
    async def is_valid_image(cls, image: UploadFile) -> JSONResponse | bool:
        """
        Проверка расширения файла
        :return: Если расширение доступно возвращает True
        """
        try:
            valid_extensions = image.filename.split(".")[-1] in cls.VALID_EXTENSIONS

            # 1 мегабайт
            max_size_image = 1_048_576

            if (image.size > max_size_image) or not valid_extensions:
                logger_error.error(f"Size image {image.size}. User try upload {str(image)}")
                return JSONResponse(
                    status_code=400, content={"detail": "Invalid image"}
                )

        except Exception as e:
            logger_error.error(f"Error in is_valid_image {str(e)}")

        return False


class ResizeImage:
    @staticmethod
    def resize_image(file_path: str, image_path_resize: str):
        """
        Уменьшает размер изображения
        """
        try:
            image = Path(file_path)
            img = Image.open(image)

            max_size = (72, 72)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            with open(image_path_resize, "wb") as file:
                img.save(file, format="WebP", lossless=True, quality=100, method=6)
        except Exception as e:
            logger_error.error(f"Error in resize_image: {str(e)}")


class ImagePathUpdater:
    @classmethod
    async def update_file_path_user(cls, user_id, image_path):
        """
        Обновление изображения пользователя
        """
        await ImageOrm.update_data(user_id, image_path=image_path[5:])


class ImageService:
    @classmethod
    async def save_image(
            cls, token: str, image: UploadFile, background_tasks: BackgroundTasks
    ):
        """
        Принимает изображение, сохраняет изображение и уменьшает его размер.
        Возвращает сообщение об успешном сохранении
        """

        data_image = await ValidImage.is_valid_image(image)
        if data_image:
            return data_image

        user_id = DecodeJWT.decode_jwt(token)
        image_path_original = f"/core/static/original_images/original_{user_id}.webp"
        image_path_resize = f"/core/static/resize_images/resize_image_user_{user_id}.webp"

        with open(image_path_original, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)

        # выполняется в фоновом режиме
        background_tasks.add_task(ResizeImage.resize_image, image_path_original, image_path_resize)
        background_tasks.add_task(ImagePathUpdater.update_file_path_user, user_id, image_path_resize)
