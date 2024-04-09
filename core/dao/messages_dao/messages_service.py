import json

from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from core.schemas.message_schemas import WebSocketData
from core.chat.users.auth import decode_jwt_user_id
from core.dao.messages_dao.messages_dao import MessagesDao
from core.dao.users_dao.user_dao import UserDao
from core.chat.chat_websoket.web_socket import manager
from core.dao.image_dao.image_dao import ImageDao


class MessageService:

    @classmethod
    async def show_messages_data(cls):
        """

        :return:
        """

        return await MessagesDao.show_all_data()

    @classmethod
    async def create_connect(cls, websocket: WebSocket):
        """

        :param websocket:
        :return:
        """
        # подключение к websocket
        await manager.connect(websocket)

        try:
            while True:
                # принятие от клиента сообщения, в виде json
                data_json = await websocket.receive_text()
                print("Принятие json")
                # с помощью pydantic можем обращаться к токену и сообщению по отдельности
                # т.к это все идет в виде строки
                print("Десериализация")
                websocket_data = WebSocketData.parse_raw(data_json)

                # переменные с id пользователем и сообщением пользователя
                print("Декодирование токена")
                user_id = decode_jwt_user_id(websocket_data.token)
                user_message = websocket_data.message

                print("добавляем сообщение в базу данных")
                # добавляем сообщение в базу данных
                date_sender = await cls.add_message_db(user_message, user_id)

                print("сериализация данных в json")
                # сериализация данных в json
                data_send = await cls.serialization_data(user_id, user_message, date_sender)

                # отправка данных персонально (клиенту)
                print("отправка данных персонально (клиенту)")
                await manager.send_personal_message(data_send, websocket)

                # отправка данных всем подключенным
                print("отправка данных всем подключенным")
                await manager.broadcast(data_send, websocket)

        except (WebSocketDisconnect, Exception) as e:
            if isinstance(e, WebSocketDisconnect):
                manager.disconnect(websocket)
                await manager.broadcast(json.dumps({"event": "Client left the chat"}))
            if isinstance(e, Exception):
                print(str(e))

    @staticmethod
    async def add_message_db(message: str, user_id: int):
        """

        :param message:
        :param user_id:
        :return:
        """
        current_time = datetime.now().time()

        formatted_time = current_time.strftime("%H:%M:%S")
        time_object = datetime.strptime(formatted_time, '%H:%M:%S').time()

        await MessagesDao.insert_data(user_id=user_id, message=message,
                                      time_sent=time_object)
        return str(formatted_time)

    @staticmethod
    async def serialization_data(user_id: int, message: str, date_send):
        """

        :param user_id:
        :param message:
        :return:
        """
        data_user = await UserDao.found_name_by_id(user_id)
        file_path = await ImageDao.file_path(user_id)
        # дата
        # "https://sun9-29.userapi.com/impg/pz9-fVteFIutK6Sv301oGwJ2R3zqvCLD2eNfhw/ibCOtsp660k.jpg?size=900x1273&quality=95&sign=19b109da64ca92935675a770365a4d0a&type=album"
        data = {"username": data_user["name"], "image": file_path["image_path"], "message": message,
                "data_send": date_send, "who_sender": False}

        return json.dumps(data)
