from jose import ExpiredSignatureError, JWTError, jwt
from fastapi import Request, HTTPException, Depends
from datetime import datetime, timedelta
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


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=404, detail="Not found cookies")
    return token


async def decode_jwt(token=Depends(get_token)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        return payload
    except (ExpiredSignatureError, JWTError) as e:
        if isinstance(e, ExpiredSignatureError):
            raise HTTPException(status_code=401, detail="The access token has expired")
        if isinstance(e, JWTError):
            raise HTTPException(status_code=401, detail="Invalid access token format")


def wb_decode_jwt(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        return int(payload.get("sub"))
    except (ExpiredSignatureError, JWTError) as e:
        if isinstance(e, ExpiredSignatureError):
            raise HTTPException(status_code=401, detail="The access token has expired")
        if isinstance(e, JWTError):
            raise HTTPException(status_code=401, detail="Invalid access token format")
