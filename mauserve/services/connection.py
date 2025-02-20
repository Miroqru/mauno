from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel


class NotifyManager:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)
        logger.info("New client, now {} clients", len(self.clients))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.clients:
            self.clients.remove(websocket)
        logger.info("Client disconnect, now {} clients", len(self.clients))

    async def push(self, message: BaseModel):
        for connection in self.clients:
            try:
                await connection.send_text(message.model_dump_json())
            except Exception as e:
                logger.error(e)
