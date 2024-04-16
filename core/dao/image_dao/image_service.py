import shutil
from pathlib import Path
from PIL import Image
from fastapi import UploadFile
from fastapi.responses import JSONResponse

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
    def save_resize_image(cls, token: str, image: UploadFile):
        """
        Принимает изображение, сохраняет изображение и уменьшает его размер.
        Возвращает сообщение об успешном сохранении
        """

        if not cls.is_valid_extension(image):
            logger_error.error(f"User try upload {str(image)}")
            return JSONResponse(status_code=400, content={"detail": "Invalid extension"})

        user_id = decode_jwt_user_id(token)
        file_path = f"/core/static/original_images/original_{user_id}.webp"

        with open(file_path, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)


        cls.resize_image(file_path, user_id)
        cls.update_data(user_id,file_path)

        return {"message": "Image installed successfully"}

    @staticmethod
    def resize_image(file_path: str, user_id: int):

        image = Path(file_path)
        img = Image.open(image)

        max_size = (72, 72)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        image_path = f"/core/static/resize_images/resize_image_user_{user_id}.webp"

        with open(image_path, "wb") as file:
            img.save(file, format="WebP", lossless=True, quality=100, method=6)

    @classmethod
    async def update_data(self, user_id, image_path):
        await ImageDao.update_data(user_id,image_path=image_path)

