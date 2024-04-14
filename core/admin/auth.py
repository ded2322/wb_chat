from typing import Union
from jose import jwt, ExpiredSignatureError, JWTError
from datetime import datetime, timedelta

from jwt import DecodeError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse

from core.config import settings


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        name, password = form["username"], form["password"]

        if not (settings.ADMIN_NAME == name or settings.ADMIN_PASSWORD == password):
            return False

        admin_token = create_access_token({"sub": name})
        request.session.update({"admin_token": admin_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Union[Response, bool]:
        token = request.session.get("admin_token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        user = decode_jwt(token)
        if not user:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True


def decode_jwt(token: str) -> str | JSONResponse:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        return payload.get("sub")
    except (ExpiredSignatureError, JWTError, DecodeError) as e:
        if isinstance(e, ExpiredSignatureError):
            return JSONResponse(status_code=401, content={"detail": "The access token has expired"})
        if isinstance(e, JWTError):
            return JSONResponse(status_code=401, content={"detail": "Invalid access token format"})
        if isinstance(e, DecodeError):
            return JSONResponse(status_code=401, content={"detail": str(e)})


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY)


authentication_backend = AdminAuth(secret_key="...")
