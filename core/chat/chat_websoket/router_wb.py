from fastapi import APIRouter, WebSocket

from core.dao.websocket_service.web_socket_service import WebsocketService

router = APIRouter(prefix="", tags=["Websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await WebsocketService.create_connect(websocket)
