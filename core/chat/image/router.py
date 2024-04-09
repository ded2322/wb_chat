from fastapi import APIRouter, UploadFile

from core.dao.image_dao.image_service import ImageService

router = APIRouter(
    prefix="/avatar",
    tags=["Upload image"]
)


@router.post("/upload", status_code=201, summary="Update avatar user")
async def upload_avatar(token: str, image: UploadFile):
    """
    Загрузка своего собственного аватара (изображения)
    :param token: Принимает в url jwt-token
    :param image: Принимает изображение. Доступные расширения файлов ["png", "jpg", "webp"]
    :return: При успешной установке аватара {"message": "Image installed successfully"}.
    """
    return ImageService.save_resize_image(token, image)
