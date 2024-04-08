from fastapi import APIRouter, WebSocket
from fastapi_versioning import version

from core.dao.messages_dao.messages_service import MessageService

router = APIRouter(
    prefix="",
    tags=["Chat"]
)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await MessageService.create_connect(websocket)
