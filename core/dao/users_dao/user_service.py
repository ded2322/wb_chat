import random
from fastapi.responses import JSONResponse

from core.dao.users_dao.user_dao import UserDao
from core.dao.image_dao.image_dao import ImageDao
from core.schemas.users_schemas import UserDataSchema, UserUpdateDataSchema, JWTTokenSchema
from core.chat.users.auth import get_password_hash, verification_password, create_access_token, decode_jwt_user_id
from core.logs.logs import logger_error


class UserService:
    @classmethod
    async def show_all_users(cls):
        """
        Возвращает всех пользователей. В виде списка словарей
        """
        return await UserDao.show_all_data()

    @classmethod
    async def user_info(cls, jwt_token: JWTTokenSchema):
        """
        Отдает всю информацию по пользователю.
        Возвращает в виде словаря: Имя, пароль, изображение
        """
        try:
            # Ищет информацию по пользователю
            user_info = await UserDao.select_user_info(decode_jwt_user_id(jwt_token.token))
            # Если пользователя нет, отдает ошибку
            if not user_info:
                return JSONResponse(status_code=409, content={"detail": "User not found"})
            return user_info
        except Exception as e:
            logger_error.error(f"Error in user_info: {str(e)}")

    @classmethod
    async def register_user(cls, data_user: UserDataSchema):
        """
        Регистрирует пользователя.
        Создает записи в таблице users и images.
        При регистрации случайным образом присваиваются изображения
        """
        try:
            # Ищет, есть ли пользователи с таким же именем
            if await UserDao.found_or_none_data(name=data_user.name):
                return JSONResponse(status_code=409, content={"detail": "Name is occupied"})
            # Хеширует пароль
            hash_password = get_password_hash(data_user.password)
            # Добавляет данные в таблицу
            await UserDao.insert_data(name=data_user.name, password=hash_password)
            # Присваивает аватар пользователю
            await cls.avatar_user(data_user.name)

            return {"message": "User registered successfully"}

        except Exception as e:
            logger_error.error(f"Error in register_user: {str(e)}")

    @classmethod
    async def login_user(cls, data_user: UserDataSchema):
        """
        Аутентификация пользователя.
        Возвращает токен в словаре.
        """
        try:
            # Проверяет валидность имени и пароля
            user = await UserDao.found_or_none_data(name=data_user.name)
            if not user or not verification_password(data_user.password, user["password"]):
                return JSONResponse(status_code=409, content={"detail": "Invalid credentials"})

            # Создается токен доступа
            jwt_token = create_access_token({"sub": str(user.id)})

            return {"token": jwt_token}

        except Exception as e:
            logger_error.error(str(e))

    @classmethod
    async def update_data_user(cls, data_update: UserUpdateDataSchema, jwt_token: JWTTokenSchema):
        """
        Обновляет данные пользователя на основе предоставленной информации.

        :param data_update: Схема данных для обновления пользователя (UserUpdateDataSchema).
        :param jwt_token: Схема токена JWT (JWTTokenSchema).
        :return: JSON-ответ с сообщением об успешном обновлении данных или сообщение об ошибке.
        """
        try:
            # Получаем данные пользователя на основе расшифрованного идентификатора пользователя из токена JWT
            user_data = await UserDao.found_or_none_data(id=decode_jwt_user_id(jwt_token.token))

            # Если данные пользователя не найдены, возвращаем JSON-ответ с сообщением об ошибке
            if not user_data:
                return JSONResponse(status_code=409, content={"detail": "User not found"})

            # Создаем словарь для хранения обновляемых полей и их значений
            update_fields = {}

            # Если предоставлено новое имя пользователя
            if data_update.name:
                # Проверяем, занято ли уже такое имя другим пользователем
                if await UserDao.found_or_none_data(name=data_update.name):
                    return JSONResponse(status_code=409, content={"detail": "Name is occupied"})
                # Добавляем новое имя в словарь обновляемых полей
                update_fields["name"] = data_update.name

            # Если предоставлен новый пароль
            if data_update.password:
                # Хешируем новый пароль
                hash_password = get_password_hash(data_update.password)
                # Добавляем хешированный пароль в словарь обновляемых полей
                update_fields["password"] = hash_password

            # Если есть обновляемые поля
            if update_fields:
                # Обновляем данные пользователя в базе данных
                await UserDao.update_data(id=user_data["id"], **update_fields)

            # Возвращаем сообщение об успешном обновлении данных
            return {"message": "Data updated successfully"}
        except Exception as e:
            # Логируем сообщение об ошибке, если возникло исключение
            logger_error.error(f"Error in update_data_user: {str(e)}")

    @classmethod
    async def delete_user(cls, jwt_token: JWTTokenSchema):
        """
        Удаляет пользователя, на основе его токена.
        Пользователю присваивается хеш в виде ника, и создается хеш пароль.
        Изображение ставится по умолчанию
        """
        try:
            user_id = decode_jwt_user_id(jwt_token.token)
            user_data = await UserDao.found_or_none_data(id=user_id)

            if not user_data:
                return JSONResponse(status_code=409, content={"detail": "User not found"})

            new_data = str(hash(user_data["name"] + user_data["password"]))
            update_fields = {"name": new_data[:3], "password": new_data}

            await UserDao.update_data(id=user_id, **update_fields)

            image_path = "https://sun9-29.userapi.com/impg/pz9-fVteFIutK6Sv301oGwJ2R3zqvCLD2eNfhw/ibCOtsp660k.jpg?size=900x1273&quality=95&sign=19b109da64ca92935675a770365a4d0a&type=album"
            await ImageDao.update_data(id=user_id, image_path=image_path)

            return {"message": "User deleted successfully"}
        except Exception as e:
            logger_error.error(f"Error in delete_user: {str(e)}")

    @staticmethod
    async def avatar_user(name):
        """
        Случайно выбирает аватар пользователю.
        Создает запись в таблице, с id пользователя и путем до изображения
        """
        list_avatar = [1, 2, 3, 4, 5]

        number_avatar = random.choice(list_avatar)
        image_path = f"core/static/image_default/image_default_{number_avatar}.webp"
        try:
            user_info = await UserDao.found_data_by_column("id", name=name)
            await ImageDao.insert_data(user_id=user_info["id"], image_path=image_path)
        except Exception as e:
            logger_error.error(f"Error in avatar_user: {str(e)}")
