from pydantic import BaseModel


class WebSocketDataSchema(BaseModel):
    token: str
    message: str


class MessageSchema(BaseModel):
    id_message: int


class MessageDeleteSchema(BaseModel):
    token: str
    id_message: int


class MessageUpdateSchema(BaseModel):
    token: str
    message_id: int
    message: str
