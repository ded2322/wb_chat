from fastapi import APIRouter, BackgroundTasks, UploadFile

from core.layers.image_layer import ImageService
from core.logs.logs import logger_response

router = APIRouter(prefix="/avatar", tags=["Upload image"])


@router.post("/upload", status_code=201, summary="Update avatar user")
async def upload_avatar(
    token: str, image: UploadFile, background_tasks: BackgroundTasks
):
    """
    Загрузка своего собственного аватара (изображения)
    :param background_tasks:
    :param token: Принимает в url jwt-token
    :param image: Принимает изображение. Доступные расширения файлов ["png", "jpg", "webp"]
    :return: При успешной установке аватара {"message": "Image installed successfully"}.
    """
    logger_response.info("User upload image")
    await ImageService.save_image(token, image, background_tasks)
    return {"message": "Image sent for resize"}
