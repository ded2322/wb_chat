from fastapi import APIRouter

from core.layers.user_layer import UserLayer
from core.logs.logs import logger_response
from core.schemas.users_schemas import (JWTTokenSchema, UserDataLoginSchema,
                                        UserDataRegisterSchema,
                                        UserUpdateDataSchema)

router_auth = APIRouter(prefix="/auth", tags=["Auth"])

router_user = APIRouter(prefix="/user", tags=["User"])


@router_auth.post("/register-admin", status_code=201, summary="Register admin")
async def register_admin(data_user: UserDataRegisterSchema):
    """
    Регистрирует админа
    :param data_user:
    :return:
    """
    logger_response.info("Register admin")
    return await UserLayer.register_user(data_user, default_user=False)


@router_auth.post("/register-user", status_code=201, summary="Register user")
async def register_default_user(data_user: UserDataRegisterSchema):
    """
    Позволяет создавать пользователя.
    Все параметры обязательны.
    :return: Если успешно 201 статус код. Json с сообщением
    """
    logger_response.info("User registered")
    return await UserLayer.register_user(data_user)


@router_user.get("/all", status_code=200, summary="Show all users")
async def all_user():
    """
    Возвращает данные всех пользователей
    :return: Если успешно 200 статус код. Данные в виде json
    """
    logger_response.info("Show all user")
    return await UserLayer.show_all_users()


@router_user.post("/me", status_code=200, summary="Show info about user")
async def user_info(jwt_token: JWTTokenSchema):
    """
    Возвращает данные по конкретному пользователю. На основе его jwt.
    :param: Использует jwt token принимаемый в виде json.
    :return: Если успешно 200 статус код. json с данным пользователя
    """
    logger_response.info("Show info user")
    return await UserLayer.user_info(jwt_token)


@router_user.post("/login", status_code=200, summary="Login user")
async def login_user(data_user: UserDataLoginSchema):
    """
    Аутентификация пользователя
    :param: Все параметры обязательны.
    :return: Возвращает json с jwt токеном пользователя. При успешном входе 201 статус код.
    """
    logger_response.info("User is login")
    return await UserLayer.login_user(data_user)


@router_user.patch("/update", status_code=201, summary="Update data user")
async def update_data_user(
    jwt_token: JWTTokenSchema, data_update: UserUpdateDataSchema
):
    """
    Обновляет данные пользователя, все поля опциональным
    :param: Для успешного обновления нужно передать jwt token
    :return: Возвращает json с сообщением. При успешном обновлении 201 статус код.
    """
    logger_response.info("User update data")
    return await UserLayer.update_data_user(data_update, jwt_token)


@router_user.delete("/delete", status_code=201, summary="Delete user")
async def delete_user(jwt_token: JWTTokenSchema):
    """
    Удаляет аккаунт
    :param: Для успешного обновления нужно передать jwt token
    :return: Если успешно 204 статус код
    """
    logger_response.info("User deleted")
    return await UserLayer.delete_user(jwt_token)
