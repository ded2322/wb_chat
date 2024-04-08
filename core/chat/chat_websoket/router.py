from fastapi import APIRouter

from core.dao.messages_dao.messages_service import MessageService


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


'''@router.patch("/update")
async def update_messages():
    """
    В разработке
    """
    ...


@router.delete("/delete")
async def delete_messages():
    """
    В разработке
    """
    ...
'''