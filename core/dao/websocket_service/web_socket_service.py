import json
import time
from datetime import datetime

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from core.chat.chat_websoket.web_socket import manager
from core.chat.users.auth import decode_jwt_user_id
from core.dao.image_dao.image_dao import ImageDao
from core.dao.messages_dao.messages_dao import MessagesDao
from core.dao.users_dao.user_dao import UserDao
from core.logs.logs import logger_websocket
from core.schemas.message_schemas import WebSocketDataSchema


class WebsocketDecodeJWT:
    @staticmethod
    def decode_jwt(jwt_token: str) -> int:
        return int(decode_jwt_user_id(jwt_token))


class WebsocketSerializer:
    @staticmethod
    async def serialize_message(user_id: int, message: str, date_send):
        """
        Сериализует данные в json.
        Возвращает json с ником, изображение, сообщением, датой отправки, ?с какой стороны сообщение?
        """
        data_user = await UserDao.found_or_none_data(id=user_id)
        file_path = await ImageDao.found_data_by_column("image_path", user_id=user_id)

        data = {
            "role": data_user["role"],
            "name": data_user["name"],
            "user_avatar": file_path["image_path"],
            "message": message,
            "time_send": date_send,
            "user_side": True,
        }

        return data


class WebsocketMessageAddDB:
    @staticmethod
    async def add_message_db(user_id: int, message: str):
        """
        Добавляет данные в базу данных.
        Возвращает время когда было отправлено сообщение
        """
        current_time = datetime.now().time()

        formatted_time = current_time.strftime("%H:%M:%S")
        time_object = datetime.strptime(formatted_time, "%H:%M:%S").time()

        # Добавляем в базу данных сообщение
        await MessagesDao.insert_data(
            user_id=user_id, message=message, time_send=time_object
        )
        return formatted_time


class WebsocketService:
    @classmethod
    async def create_connect(cls, websocket: WebSocket):
        """
        Создает коннект с сокетом
        :param websocket:
        :return:
        """
        async with manager.manage_connection(websocket):
            start = time.time()
            logger_websocket.info("User connected")

            try:
                while True:
                    data_json = await websocket.receive_text()
                    try:
                        websocket_data = WebSocketDataSchema.parse_raw(data_json)
                    except ValidationError as e:
                        logger_websocket.error(f"Invalid message format: {str(e)}")
                        continue

                    user_id = WebsocketDecodeJWT.decode_jwt(websocket_data.token)
                    message_input = websocket_data.message

                    await cls.process_message(user_id, message_input, websocket)

                    end = time.time()
                    print(end - start)
            except WebSocketDisconnect:
                logger_websocket.info("User disconnected")
            except Exception as e:
                logger_websocket.error(f"Error in create_connect: {str(e)}")

    @classmethod
    async def process_message(cls, user_id: int, message: str, websocket: WebSocket):
        """
        Отправляет сообщения по веб сокету
        """
        try:
            date_sender = await WebsocketMessageAddDB.add_message_db(user_id, message)
            data_send = await WebsocketSerializer.serialize_message(
                user_id, message, date_sender
            )

            # Проверяем, что соединение все еще активно перед отправкой сообщения
            if websocket.client_state.name == "CONNECTED":
                await manager.send_personal_message(json.dumps(data_send), websocket)
                data_send["user_side"] = False
                await manager.broadcast(json.dumps(data_send), websocket)
            else:
                logger_websocket.warning("Skipped sending message to closed connection")

        except Exception as e:
            logger_websocket.error(f"Error processing message: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
