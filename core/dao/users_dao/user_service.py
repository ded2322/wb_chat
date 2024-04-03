from fastapi import Response
from fastapi.responses import JSONResponse

from core.dao.users_dao.user_dao import UserDao
from core.schemas.users_schemas import UserDataSchema, UserUpdateDataSchema
from core.chat.users.auth import get_password_hash, verification_password, create_access_token, decode_jwt


class UserService:
    @classmethod
    async def show_all_users(cls):
        return await UserDao.show_all_data()

    @classmethod
    async def user_info(cls, jwt_token):
        try:
            user_info = await UserDao.found_or_none_data(id=int(jwt_token["sub"]))
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
            return {"message": "Successful register"}

        except Exception as e:
            return str(e)

    @classmethod
    async def login_user(cls, response: Response, data_user: UserDataSchema):
        try:
            user = await UserDao.found_or_none_data(name=data_user.name)
            if not user or not verification_password(data_user.password, user["password"]):
                return JSONResponse(status_code=409, content={"detail": "Invalid name or password"})

            jwt_token = create_access_token({"sub": str(user.id)})
            response.set_cookie("access_token", jwt_token, httponly=True)

            return {"message": "Successful login"}

        except Exception as e:
            return (str(e))

    @classmethod
    async def logout_user(cls, response: Response):
        try:
            response.delete_cookie("access_token")
        except Exception as e:
            return (str(e))

    @classmethod
    async def update_data_user(cls, data_update: UserUpdateDataSchema, jwt_token):
        try:
            user_data = await UserDao.found_or_none_data(id=int(jwt_token["sub"]))
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

            return {"message": "Data Successful update"}
        except Exception as e:
            return (str(e))

    @classmethod
    async def delete_user(cls, response: Response, jwt_token):
        try:
            await UserDao.delete_data(id =int(jwt_token["sub"]))
            response.delete_cookie("access_token")
        except Exception as e:
            return (str(e))