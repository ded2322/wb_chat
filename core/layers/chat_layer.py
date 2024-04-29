import json
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from core.utils.websocket import manager
from core.utils.auth import DecodeJWT
from core.orm.image_orm import ImageOrm
from core.orm.messages_orm import MessagesOrm
from core.orm.user_orm import UserOrm
from core.logs.logs import logger_websocket
from core.schemas.message_schemas import WebSocketDataSchema


class WebsocketSerializer:
    @staticmethod
    async def serialize_message(user_id: int, message: str, date_send: list):
        """
        Сериализует данные в json.
        Возвращает json с ником, изображение, сообщением, датой отправки, ?с какой стороны сообщение?
        """
        data_user = await UserOrm.found_one_or_none(id=user_id)
        file_path = await ImageOrm.found_data_by_column("image_path", user_id=user_id)

        data = {
            "user_id": data_user["id"],
            "role": data_user["role"],
            "name": data_user["name"],
            "user_avatar": file_path["image_path"],
            "message": message,
            "message_id": date_send[1],
            "time_send": date_send[0],
        }

        return json.dumps(data)


class WebsocketMessageAddDB:
    @staticmethod
    async def add_message_db(user_id: int, message: str) -> list:
        """
        Добавляет данные в базу данных.
        Возвращает время когда было отправлено сообщение
        """
        current_time = datetime.now().time()

        formatted_time = current_time.strftime("%H:%M:%S")
        time_object = datetime.strptime(formatted_time, "%H:%M:%S").time()

        # Добавляем в базу данных сообщение
        id_column = await MessagesOrm.insert_data(
            user_id=user_id, message=message, time_send=time_object
        )
        return [formatted_time, id_column]


class WebsocketValidator:
    @classmethod
    async def validate_recent_data(cls, data_json):
        try:
            websocket_data = WebSocketDataSchema.parse_raw(data_json)

            if not await cls.check_data(websocket_data.message) or not await cls.check_data(websocket_data.token):
                return False

            return websocket_data
        except ValidationError as e:
            logger_websocket.error(f"Invalid message format: {str(e)}")
            return False

    @classmethod
    async def check_data(cls, data_check: str) -> bool:
        if not data_check.isspace():
            return True
        else:
            return False


class WebsocketService:
    @classmethod
    async def create_connect(cls, websocket: WebSocket):
        """
        Создает коннект с сокетом
        """
        async with manager.manage_connection(websocket):
            logger_websocket.info("User connected")
            try:
                while True:
                    data_json = await websocket.receive_text()

                    passing_validation = await WebsocketValidator.validate_recent_data(data_json)
                    if not passing_validation:
                        await WebsocketService.send_user_message("Invalid format", websocket)
                        await websocket.close()

                    user_id = DecodeJWT.decode_jwt(passing_validation.token)
                    if not user_id:
                        await cls.send_user_message("Invalid token", websocket)
                        break

                    message_input = passing_validation.message
                    await cls.process_message(user_id, message_input, websocket)

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
                await manager.send_personal_message(data_send, websocket)

                await manager.broadcast(data_send, websocket)
            else:
                logger_websocket.warning("Skipped sending message to closed connection")

        except Exception as e:
            logger_websocket.error(f"Error in processing message: {str(e)}")

    @classmethod
    async def send_user_message(cls, message: str, websocket: WebSocket):
        """
        Отправляем сообщение персонально пользователю
        """
        data_send = {"event": "send user message", "message": message}
        if websocket.client_state.name == "CONNECTED":
            await manager.send_personal_message(json.dumps(data_send), websocket)
            await websocket.close()
