import random

from fastapi.responses import JSONResponse

from core.utils.auth import (create_access_token, DecodeJWT,
                             get_password_hash, verification_password)
from core.orm.image_orm import ImageOrm
from core.orm.user_orm import UserOrm
from core.logs.logs import logger_error
from core.schemas.users_schemas import (JWTTokenSchema, UserDataLoginSchema,
                                        UserDataRegisterSchema,
                                        UserUpdateDataSchema)


class UserCheck:
    @classmethod
    async def check_username_exists(cls, **kwargs):
        user_data = await UserOrm.found_one_or_none(**kwargs)

        if user_data:
            return True

        return False

    @classmethod
    async def get_user_info(cls, **kwargs) -> dict | bool:
        """
        Возвращает информацию о пользователе по заданным критериям
        """
        user_data = await UserOrm.found_one_or_none(**kwargs)
        if not user_data:
            return False
        return user_data


class UserAvatar:
    @classmethod
    async def avatar_user(cls, name: str):
        """
        Случайно выбирает аватар пользователю.
        Создает запись в таблице, с id пользователя и путем до изображения
        """

        try:
            user_info = await UserOrm.found_data_by_column("id", name=name)
            image_path = cls.get_random_avatar()
            await ImageOrm.insert_data(user_id=user_info["id"], image_path=image_path)
        except Exception as e:
            logger_error.error(f"Error in avatar_user: {str(e)}")

    @staticmethod
    def get_random_avatar():
        """
        Возвращает случайный путь к аватару.
        """
        list_avatar = list(range(1, 20))

        number_avatar = random.choice(list_avatar)
        image_path = f"/static/image_default/image_default_{number_avatar}.webp"
        return image_path


class UserValidator:
    @classmethod
    async def register_user_validator(cls,
                                      data_user: UserDataRegisterSchema, default_user: bool = True
                                      ):
        # проверка на пустоту
        if await cls.check_data(data_user.name) or await UserValidator.check_data(data_user.password):
            return JSONResponse(status_code=409, content={"detail": "Field must not be empty"})

        # Ищет, есть ли пользователи с таким же именем
        if await UserCheck.check_username_exists(name=data_user.name):
            return JSONResponse(status_code=409, content={"detail": "Name is occupied"})

        if (data_user.role < 1) or (data_user.role > 3):
            return JSONResponse(status_code=409, content={"detail": "Invalid role"})

        if default_user and data_user.role > 1:
            return JSONResponse(status_code=409, content={"detail": "Invalid role"})

        return False

    @classmethod
    async def check_data(cls, data_check: str) -> bool:
        if not data_check.isspace():
            return False
        else:
            return True

    @classmethod
    async def login_user_validator(cls, user, data_user: UserDataLoginSchema):
        # Проверяет валидность имени и пароля

        if not user or not verification_password(
                data_user.password, user["password"]
        ):
            return True
        return False

    @classmethod
    def update_data_user_validator(cls, user_data):
        if not user_data:
            return JSONResponse(
                status_code=409, content={"detail": "User not found"}
            )

        return False


class UserLayer:
    @classmethod
    async def show_all_users(cls):
        """
        Возвращает всех пользователей. В виде списка словарей
        """
        return await UserOrm.show_all_data()

    @classmethod
    async def user_info(cls, jwt_token: JWTTokenSchema):
        """
        Отдает всю информацию по пользователю.
        Возвращает в виде словаря: Имя, пароль, изображение
        """
        try:
            # Ищет информацию по пользователю
            user_info = await UserOrm.user_info(DecodeJWT.decode_jwt(jwt_token.token))
            # Если пользователя нет, отдает ошибку
            if not user_info:
                return JSONResponse(status_code=409, content={"detail": "User not found"})
            return user_info
        except Exception as e:
            logger_error.error(f"Error in user_info: {str(e)}")

    @classmethod
    async def register_user(
            cls, data_user: UserDataRegisterSchema, default_user: bool = True
    ):
        """
        Регистрирует пользователя.
        Создает записи в таблице users и images.
        При регистрации случайным образом присваиваются изображения
        """
        try:
            # валидация данных, проверка, что имя не занято, корректная роль, не пустые поля
            validator = await UserValidator.register_user_validator(data_user, default_user)
            if validator:
                # если не проходит возвращает ошибку
                return validator

            # Хеширует пароль
            hash_password = get_password_hash(data_user.password)

            # Добавляет данные в таблицу
            await UserOrm.insert_data(name=data_user.name, password=hash_password, role=data_user.role)

            # Присваивает аватар пользователю
            await UserAvatar.avatar_user(data_user.name)

            return {"message": "User registered successfully"}
        except Exception as e:
            logger_error.error(f"Error in register_default_user: {str(e)}")

    @classmethod
    async def login_user(cls, data_user: UserDataLoginSchema):
        """
        Аутентификация пользователя.
        Возвращает токен в словаре.
        """
        try:
            # проверка есть ли пользователь в бд
            user = await UserCheck.get_user_info(name=data_user.name)
            # проверка пароля
            if await UserValidator.login_user_validator(user, data_user):
                return JSONResponse(status_code=409, content={"detail": "Invalid credentials"})

            # Создается токен доступа
            jwt_token = create_access_token({"sub": str(user["id"])})

            return {"token": jwt_token, "user_id": user["id"]}

        except Exception as e:
            logger_error.error(f"Error in login_user: {str(e)}")

    @classmethod
    async def update_data_user(
            cls, data_update: UserUpdateDataSchema, jwt_token: JWTTokenSchema
    ):
        """
        Обновляет данные пользователя на основе предоставленной информации.

        :param data_update: Схема данных для обновления пользователя (UserUpdateDataSchema).
        :param jwt_token: Схема токена JWT (JWTTokenSchema).
        :return: JSON-ответ с сообщением об успешном обновлении данных или сообщение об ошибке.
        """
        try:
            # Получаем данные пользователя на основе расшифрованного идентификатора пользователя из токена JWT
            user_data = await UserCheck.get_user_info(id=DecodeJWT.decode_jwt(jwt_token.token))

            # Если данные пользователя не найдены, возвращаем JSON-ответ с сообщением об ошибке
            data_validator = UserValidator.update_data_user_validator(user_data)
            if data_validator:
                return data_validator

            # Создаем словарь для хранения обновляемых полей и их значений
            update_fields = {}

            #  Если предоставлено новое имя
            if data_update.name:
                if await UserOrm.found_one_or_none(name=data_update.name):
                    return JSONResponse(
                        status_code=409, content={"detail": "Name is occupied"}
                    )
                # Добавляем новое имя в словарь обновляемых полей
                update_fields["name"] = data_update.name

            # Если предоставлен новый пароль
            if data_update.password:
                hash_password = get_password_hash(data_update.password)
                update_fields["password"] = hash_password

            # Если есть обновляемые поля
            if update_fields:
                await UserOrm.update_data(id=user_data["id"], **update_fields)

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
            user_data = await UserCheck.get_user_info(id=DecodeJWT.decode_jwt(jwt_token.token))

            if not user_data:
                return user_data
            password = get_password_hash(user_data["password"])
            update_fields = {
                "name": f"Удаленный # {user_data['id']}",
                "password": password,
            }

            await UserOrm.update_data(id=user_data['id'], **update_fields)

            image_path = "https://sun9-29.userapi.com/impg/pz9-fVteFIutK6Sv301oGwJ2R3zqvCLD2eNfhw/ibCOtsp660k.jpg?size=900x1273&quality=95&sign=19b109da64ca92935675a770365a4d0a&type=album"
            await ImageOrm.update_data(id=user_data['id'], image_path=image_path)

            return {"message": "User deleted successfully"}
        except Exception as e:
            logger_error.error(f"Error in delete_user: {str(e)}")
