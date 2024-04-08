import random
from fastapi.responses import JSONResponse

from core.dao.users_dao.user_dao import UserDao
from core.dao.image_dao.image_dao import ImageDao
from core.schemas.users_schemas import UserDataSchema, UserUpdateDataSchema, JWTTokenSchema
from core.chat.users.auth import get_password_hash, verification_password, create_access_token, decode_jwt_user_id


class UserService:
    @classmethod
    async def show_all_users(cls):
        return await UserDao.show_all_data()

    @classmethod
    async def user_info(cls, jwt_token: JWTTokenSchema):
        try:
            user_info = await UserDao.select_user_info(decode_jwt_user_id(jwt_token.token))
            if not user_info:
                return JSONResponse(status_code=409, content={"detail": "User not found"})
            return user_info
        except Exception as e:
            return (str(e))

    @classmethod
    async def register_user(cls, data_user: UserDataSchema):
        try:
            if await UserDao.found_or_none_data(name=data_user.name):
                return JSONResponse(status_code=409, content={"detail": "Name is occupied"})

            hash_password = get_password_hash(data_user.password)
            await UserDao.insert_data(name=data_user.name, password=hash_password)

            await cls.avatar_user(data_user.name)

            return {"message": "User successful register"}

        except Exception as e:
            return str(e)

    @classmethod
    async def login_user(cls, data_user: UserDataSchema):
        try:
            user = await UserDao.found_or_none_data(name=data_user.name)
            if not user or not verification_password(data_user.password, user["password"]):
                return JSONResponse(status_code=409, content={"detail": "Invalid name or password"})

            jwt_token = create_access_token({"sub": str(user.id)})

            return {"token": jwt_token}

        except Exception as e:
            return (str(e))

    @classmethod
    async def update_data_user(cls, data_update: UserUpdateDataSchema, jwt_token: JWTTokenSchema):
        try:
            user_data = await UserDao.found_or_none_data(id=decode_jwt_user_id(jwt_token.token))
            if not user_data:
                return JSONResponse(status_code=409, content={"detail": "User not found"})

            if data_update.name:
                if await UserDao.found_or_none_data(name=data_update.name):
                    return JSONResponse(status_code=409, content={"detail": "Name is occupied"})

                await UserDao.update_data(id=user_data["id"], column="name", new_data=data_update.name)

            if data_update.password:
                hash_password = get_password_hash(data_update.password)

                await UserDao.update_data(id=user_data["id"],
                                          column="password",
                                          new_data=hash_password)

            return {"message": "Data successful update"}
        except Exception as e:
            return (str(e))

    @classmethod
    async def delete_user(cls, jwt_token: JWTTokenSchema):
        try:
            await UserDao.delete_data(id=decode_jwt_user_id(jwt_token.token))
        except Exception as e:
            return (str(e))

    @staticmethod
    async def avatar_user(name):
        """

        :param name:
        :return:
        """
        list_avatar = [1, 2, 3, 4, 5]

        number_avatar = random.choice(list_avatar)
        image_path = f"core/static/image_default/image_default_{number_avatar}.webp"

        user_info = await UserDao.found_id_by_name(name=name)

        await ImageDao.insert_data(user_id=user_info["id"], image_path=image_path)
