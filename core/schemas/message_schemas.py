from pydantic_settings import BaseSettings
from pydantic import BaseModel


class MessageSchema(BaseSettings):
    message: str


class WebSocketData(BaseModel):
    token: str
    message: str
