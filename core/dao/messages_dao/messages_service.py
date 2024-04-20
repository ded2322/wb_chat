import json
import time
from datetime import datetime

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.chat.chat_websoket.web_socket import manager
from core.chat.users.auth import decode_jwt_user_id
from core.dao.image_dao.image_dao import ImageDao
from core.dao.messages_dao.messages_dao import MessagesDao
from core.dao.users_dao.user_dao import UserDao
from core.logs.logs import logger_websocket
from core.schemas.message_schemas import (MessageDeleteSchema, MessageSchema,
                                          MessageUpdateSchema,
                                          WebSocketDataSchema)


class MessageDecodeJWT:
    @staticmethod
    def decode_jwt(jwt_token: str) -> int:
        return int(decode_jwt_user_id(jwt_token))


class MessageService:

    @classmethod
    async def show_messages_data(cls):
        """
        Отображает последние 50 сообщений.
        :return: Список словарей
        """
        return await MessagesDao.show_all_data()

    @classmethod
    async def load_message(cls, id_message: MessageSchema):
        """
        Загружает дополнительно 50 сообщений.
        Принимает id последнего сообщения.
        :return: Список словарей
        """
        return await MessagesDao.load_messages(id_message.id_message)

    @classmethod
    async def update_message(cls, user_message_data: MessageUpdateSchema):
        """
        Обновляет сообщение пользователя
        """
        try:
            user_id = MessageDecodeJWT.decode_jwt(user_message_data.token)
            message_data = await MessagesDao.found_or_none_data(
                id=user_message_data.message_id
            )

            if not message_data:
                return JSONResponse(
                    status_code=409, content={"detail": "Message not found"}
                )
            if not (message_data["user_id"] == user_id):
                return JSONResponse(
                    status_code=409, content={"detail": "Unauthorized access"}
                )

            await MessagesDao.update_data(
                user_message_data.message_id, message=user_message_data.message
            )
            data = {
                "event": "update",
                "message_id": user_message_data.message_id,
                "new_message": user_message_data.message,
            }

            await manager.broadcast_event(json.dumps(data))
            return {"message": "message updated successfully"}
        except Exception as e:
            logger_websocket.error(f"Error in update_message: {str(e)}")

    @classmethod
    async def delete_message(cls, message: MessageDeleteSchema):
        """
        Удаляет сообщение пользователя
        """
        try:
            user_id = MessageDecodeJWT.decode_jwt(message.token)
            user_data = await UserDao.found_or_none_data(id=user_id)

            if user_data["role"] < 2:
                return JSONResponse(
                    status_code=409, content={"detail": "Unauthorized access"}
                )

            message_data = await MessagesDao.found_or_none_data(id=message.id_message)

            if not message_data:
                return JSONResponse(
                    status_code=409, content={"detail": "Message not found"}
                )

            await MessagesDao.delete_data(id=message.id_message)

            data = {"event": "delete", "message_id": message.id_message}

            await manager.broadcast_event(json.dumps(data))

            return {"message": "message deleted successfully"}
        except Exception as e:
            logger_websocket.error(f"Error in delete_message: {str(e)}")
