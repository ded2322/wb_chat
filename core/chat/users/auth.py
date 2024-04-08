from jose import ExpiredSignatureError, JWTError, jwt
from fastapi import Request, HTTPException, Depends
from datetime import datetime, timedelta

from jwt import DecodeError
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verification_password(input_password, hashed_password) -> bool:
    return pwd_context.verify(input_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_jwt_user_id(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        return int(payload.get("sub"))
    except (ExpiredSignatureError, JWTError, DecodeError) as e:
        if isinstance(e, ExpiredSignatureError):
            raise HTTPException(status_code=401, detail="The access token has expired")
        if isinstance(e, JWTError):
            raise HTTPException(status_code=401, detail="Invalid access token format")
        if isinstance(e, DecodeError):
            raise HTTPException(status_code=401, detail="TOKEN")