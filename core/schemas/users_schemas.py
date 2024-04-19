from typing import Optional

from pydantic import BaseModel


class UserDataRegisterSchema(BaseModel):
    role: int = 1
    name: str
    password: str


class UserDataLoginSchema(BaseModel):
    name: str
    password: str


class JWTTokenSchema(BaseModel):
    token: str


class UserUpdateDataSchema(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
