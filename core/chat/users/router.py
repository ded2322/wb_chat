from fastapi import APIRouter, Response, Depends
from fastapi_versioning import version

from core.chat.users.auth import decode_jwt
from core.schemas.users_schemas import UserDataSchema, UserUpdateDataSchema
from core.dao.users_dao.user_service import UserService

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

router_user = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router_auth.options("/void")
@version(1)
async def options_route():
    return {"message": "This route supports OPTIONS method"}


@router_auth.post("/register", status_code=201, summary="Register user")
@version(1)
async def register_user(data_user: UserDataSchema):
    """
    Позволяет создавать пользователя.
    Все параметры обязательны.
    :return: Если успешно 201 статус код. Json с сообщением
    """
    return await UserService.register_user(data_user)


@router_user.get("/all", status_code=200, summary="Show all users")
@version(1)
async def all_user():
    """
    Возвращает данные всех пользователей
    :return: Если успешно 200 статус код. Данные в виде json
    """
    return await UserService.show_all_users()


@router_user.get("/me", status_code=200, summary="Show info about user")
@version(1)
async def user_info(jwt_token=Depends(decode_jwt)):
    """
    Возвращает данные по конкретному пользователю, по его jwt.
    :param: Использует jwt token из браузера пользователя.
    :return: Если успешно 200 статус код. json с данным пользователя
    """
    return await UserService.user_info(jwt_token)


@router_user.post("/login", status_code=200, summary="Login user")
@version(1)
async def login_user(response: Response, data_user: UserDataSchema):
    """
    Аутентификация пользователя
    :param: Все параметры обязательны
    :return: Если успешно 201 статус код, json с сообщением
    """
    return await UserService.login_user(response, data_user)


@router_user.post("/logout", status_code=204, summary="Logout user")
@version(1)
async def logout_user(response: Response):
    """
    "Выход из аккаунта", просто удаляет jwt token
    :return: Если успешно 204 статус код
    """
    await UserService.logout_user(response)


@router_user.patch("/update", status_code=201, summary="Update data user")
@version(1)
async def update_name(data_update: UserUpdateDataSchema, data_jwt=Depends(decode_jwt)):
    """
    Обновляет данные пользователя, все поля опциональным
    :param: Для успешного обновления нужен jwt токен
    :return: Если успешно 201 статус код, json с данным пользователя
    """
    return await UserService.update_data_user(data_update, data_jwt)


@router_user.delete("/delete", status_code=204, summary="Delete user")
@version(1)
async def delete_user(response: Response, jwt_token=Depends(decode_jwt)):
    """
    Удаляет аккаунт и jwt токен
    :param: Для успешного обновления нужен jwt токен
    :return: Если успешно 204 статус код
    """
    await UserService.delete_user(response, jwt_token)
