import json

from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from pydantic import ValidationError

from core.schemas.message_schemas import WebSocketDataSchema
from core.chat.users.auth import decode_jwt_user_id
from core.dao.messages_dao.messages_dao import MessagesDao
from core.dao.users_dao.user_dao import UserDao
from core.chat.chat_websoket.web_socket import manager
from core.dao.image_dao.image_dao import ImageDao
from core.logs.logs import logger_websocket
from core.schemas.message_schemas import MessageLoadSchema


class MessageService:

    @classmethod
    async def show_messages_data(cls):
        """
        Отображает последние 50 сообщений.
        :return: Список словарей
        """
        return await MessagesDao.show_all_data()

    @classmethod
    async def load_message(cls, id_message: MessageLoadSchema):
        """
        Загружает дополнительно 50 сообщений.
        Принимает id последнего сообщения.
        :return: Список словарей
        """
        return await MessagesDao.load_messages(id_message.id_last_message)

    @classmethod
    async def create_connect(cls, websocket: WebSocket):
        import time
        start = time.time()
        await manager.connect(websocket)
        logger_websocket.info(f"User connected")

        try:
            while True:
                data_json = await websocket.receive_text()

                try:
                    websocket_data = WebSocketDataSchema.parse_raw(data_json)
                except ValidationError as e:
                    logger_websocket.error(f"Invalid message format: {str(e)}")
                    continue

                # переменные с id пользователем и сообщением пользователя
                user_id = decode_jwt_user_id(websocket_data.token)
                user_message = websocket_data.message

                await cls.process_message(user_id, user_message, websocket)

                end = time.time()

                print(end - start)
        except (WebSocketDisconnect, Exception) as e:
            if isinstance(e, WebSocketDisconnect):
                manager.disconnect(websocket)
                logger_websocket.info(f"User disconnected")
            if isinstance(e, Exception):
                logger_websocket.error(f"Error in create_connect: {str(e)}")

    @classmethod
    async def process_message(cls, user_id: int, message: str, websocket: WebSocket):
        try:
            date_sender = await cls.add_message_db(user_id, message)
            data_send = await cls.serialization_data(user_id, message, date_sender)

            await manager.send_personal_message(json.dumps(data_send), websocket)
            data_send["user_side"] = False
            await manager.broadcast(json.dumps(data_send), websocket)

        except Exception as e:
            logger_websocket.error(f"Error processing message: {str(e)}")

    @staticmethod
    async def add_message_db(user_id: int, message: str):
        """
        Добавляет данные в базу данных.
        Возвращает время когда было отправлено сообщение
        """
        current_time = datetime.now().time()

        formatted_time = current_time.strftime("%H:%M:%S")
        time_object = datetime.strptime(formatted_time, '%H:%M:%S').time()

        # Добавляем в базу данных сообщение
        await MessagesDao.insert_data(user_id=user_id, message=message,
                                      time_send=time_object)
        return formatted_time

    @staticmethod
    async def serialization_data(user_id: int, message: str, date_send):
        """
        Сериализует данные в json.
        Возвращает json с ником, изображение, сообщением, датой отправки, ?с какой стороны сообщение?
        """
        data_user = await UserDao.found_data_by_column("name", id=user_id)
        file_path = await ImageDao.found_data_by_column("image_path", user_id=user_id)

        data = {"name": data_user["name"],
                "image": file_path["image_path"],
                "message": message,
                "time_send": date_send,
                "user_side": True}

        return data
