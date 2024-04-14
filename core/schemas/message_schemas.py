from pydantic import BaseModel


class WebSocketDataSchema(BaseModel):
    token: str
    message: str


class MessageLoadSchema(BaseModel):
    id_last_message: int
