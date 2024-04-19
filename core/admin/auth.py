from typing import Union
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse

from core.chat.users.auth import verification_password, create_access_token, decode_jwt_user_id
from core.dao.users_dao.user_dao import UserDao
from core.logs.logs import logger_error


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> JSONResponse | bool:
        try:
            form = await request.form()
            name, password = form["username"], form["password"]

            user = await UserDao.found_or_none_data(name=name)
            if not user or not verification_password(password, user["password"]):
                return JSONResponse(status_code=409, content={"detail": "Invalid credentials"})
            if user["role"] < 3:
                return JSONResponse(status_code=409, content={"detail": "No access"})

            admin_token = create_access_token({"sub": name})
            request.session.update({"admin_token": admin_token})

            return True
        except Exception as e:
            logger_error.error(f"Error in login admin: {str(e)}")

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Union[Response, bool]:
        token = request.session.get("admin_token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        user = decode_jwt_user_id(token)
        if not user:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True


authentication_backend = AdminAuth(secret_key="...")
