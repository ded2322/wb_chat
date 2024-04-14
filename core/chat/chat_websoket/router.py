from fastapi import APIRouter

from core.dao.messages_dao.messages_service import MessageService
from core.schemas.message_schemas import MessageLoadSchema

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/last_messages", status_code=200, summary="Get last 50 messages")
async def get_last_messages():
    """
    Отдает последние 50 сообщений пользователя
    :return: json формата [{}, {}]
    """
    return await MessageService.show_messages_data()


@router.post("/load", status_code=200, summary="Load additional message")
async def load_message(id_message: MessageLoadSchema):
    """
    Загружает дополнительные 50 сообщений.
    Нужно передать id последнего сообщения
    :return: json формата [{}, {}]
    """
    return await MessageService.load_message(id_message)
