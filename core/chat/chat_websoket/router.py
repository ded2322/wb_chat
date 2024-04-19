from fastapi import APIRouter, WebSocket
from core.dao.messages_dao.messages_service import MessageService
from core.schemas.message_schemas import MessageSchema, MessageDeleteSchema, MessageUpdateSchema


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
async def load_message(id_message: MessageSchema):
    """
    Загружает дополнительные 50 сообщений.
    Нужно передать id последнего сообщения
    :return: json формата [{}, {}]
    """
    return await MessageService.load_message(id_message)


@router.patch("/update", status_code=201, summary="Update message user")
async def update_message(message_data: MessageUpdateSchema):
    """
    Обновляет сообщение пользователя.
    Нужен токен пользователя и id сообщения
    :return: По вебсокету отправляется event с сообщением.
    Возвращает словарь с сообщением. При успешном обновлении 201 статус код
    """

    return await MessageService.update_message(message_data)


@router.delete("/delete-message", status_code=201, summary="Delete message user")
async def delete_message(message_data: MessageDeleteSchema):
    """
    Позволяет удалять сообщение пользователя.
    ДОСТУПНО ТОЛЬКО С РОЛЬЮ 2 и 3
    :return: По вебсокету отправляется event с сообщением.
    Возвращает словарь с сообщением. При успешном обновлении 201 статус код
    """
    return await MessageService.delete_message(message_data)
