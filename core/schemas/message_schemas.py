from pydantic import BaseModel


class WebSocketData(BaseModel):
    token: str
    message: str
