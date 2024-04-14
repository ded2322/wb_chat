import shutil
from fastapi import UploadFile
from fastapi.responses import JSONResponse

from core.chat.users.auth import decode_jwt_user_id
from core.tasks.tasks import process_pic
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
        file_path = f"core/static/original_images/{user_id}.webp"

        with open(file_path, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)

        process_pic.delay(file_path, user_id)

        return {"message": "Image installed successfully"}
