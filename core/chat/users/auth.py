from jose import ExpiredSignatureError, JWTError, jwt
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

from jwt import DecodeError
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verification_password(input_password, hashed_password) -> bool:
    return pwd_context.verify(input_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_jwt_user_id(token: str) -> str | JSONResponse:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        return payload.get("sub")
    except (ExpiredSignatureError, JWTError) as e:
        if isinstance(e, ExpiredSignatureError):
            return JSONResponse(status_code=401, content={"detail": "The access token has expired"})
        if isinstance(e, JWTError):
            return JSONResponse(status_code=401, content={"detail": "Invalid access token format"})
