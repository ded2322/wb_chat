import shutil
from fastapi import UploadFile
from fastapi.responses import JSONResponse

from core.chat.users.auth import decode_jwt_user_id
from core.tasks.tasks import process_pic


class ImageService:

    @classmethod
    def save_resize_image(cls, token: str, image: UploadFile):
        """

        :param token:
        :param image:
        :return:
        """
        valid_extension = ["png", "jpg", "webp"]
        file_extension = image.filename.split(".")[-1]

        if not file_extension in valid_extension:
            return JSONResponse(status_code=400, content={"detail": "Invalid extension"})

        user_id = decode_jwt_user_id(token)

        file_path = f"core/static/original_images/{user_id}.webp"
        with open(file_path, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)

        process_pic.delay(file_path, user_id)

        return {"message": "Image installed successfully"}
