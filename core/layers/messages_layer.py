import json

from fastapi.responses import JSONResponse

from core.utils.websocket import manager
from core.utils.auth import DecodeJWT
from core.orm.messages_orm import MessagesOrm
from core.orm.user_orm import UserOrm
from core.logs.logs import logger_websocket
from core.schemas.message_schemas import (MessageDeleteSchema, MessageSchema,
                                          MessageUpdateSchema)


class MessageLayer:

    @classmethod
    async def show_messages_data(cls):
        """
        Отображает последние 50 сообщений.
        :return: Список словарей
        """
        return await MessagesOrm.get_message()

    @classmethod
    async def load_message(cls, id_message: MessageSchema):
        """
        Загружает дополнительно 50 сообщений.
        Принимает id последнего сообщения.
        :return: Список словарей
        """
        return await MessagesOrm.get_message(load_previous=True, message_id=id_message.id_message)

    @classmethod
    async def update_message(cls, user_message_data: MessageUpdateSchema):
        """
        Обновляет сообщение пользователя
        """
        try:
            user_id = DecodeJWT.decode_jwt(user_message_data.token)
            message_data = await MessagesOrm.found_one_or_none(id=user_message_data.message_id)

            if not message_data or message_data["user_id"] != user_id:
                return JSONResponse(
                    status_code=409, content={"detail": "Unauthorized access"}
                )

            await MessagesOrm.update_data(user_message_data.message_id,
                                          message=user_message_data.message)

            data = {"message_id": user_message_data.message_id,
                    "new_message": user_message_data.message}
            await cls.send_event("update", **data)

            return {"message": "message updated successfully"}
        except Exception as e:
            logger_websocket.error(f"Error in update_message: {str(e)}")

    @classmethod
    async def delete_message(cls, message: MessageDeleteSchema):
        """
        Удаляет сообщение пользователя
        """
        try:
            user_id = DecodeJWT.decode_jwt(message.token)
            user_data = await UserOrm.found_one_or_none(id=user_id)

            message_data = await MessagesOrm.found_one_or_none(id=message.id_message)

            if not message_data or user_data["role"] < 2:
                return JSONResponse(
                    status_code=409, content={"detail": "Unauthorized access"}
                )

            await MessagesOrm.delete_data(id=message.id_message)
            # отправка event на удаление сообщения
            event_data = {"message_id": message.id_message}
            await cls.send_event("delete", **event_data)

            return {"message": "message deleted successfully"}
        except Exception as e:
            logger_websocket.error(f"Error in delete_message: {str(e)}")

    @staticmethod
    async def send_event(event: str, **kwargs):
        data_event = {"event": event, **kwargs}
        await manager.broadcast_event(json.dumps(data_event))
