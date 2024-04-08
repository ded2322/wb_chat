from fastapi import APIRouter, UploadFile

from core.schemas.users_schemas import JWTTokenSchema
from core.dao.image_dao.image_service import ImageService

router = APIRouter(
    prefix="/avatar",
    tags=["Upload image"]
)


@router.post("/upload")
async def test(token:str, image:UploadFile):
    return ImageService.save_resize_image(token, image)
