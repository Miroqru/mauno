"""Вспомогательный модуль отправки игровых событий."""

import asyncio

from fastapi import WebSocket
from loguru import logger
from pydantic import BaseModel

from mau.events import BaseEventHandler, Event, GameEvents
from mauserve.schemes.game import (
    GameData,
    PlayerData,
    game_to_data,
    player_to_data,
)


class EventData(BaseModel):
    """Определённое игровое события на сервере.

    - event_type: Тип произошедшего события.
    - from_player: Кто совершил данное событие.
    - data: Некоторая полезная информация.
    - context: Текущий игровой контекст.
    """

    event: GameEvents
    player: PlayerData
    data: str
    game: GameData


class WebSocketEventHandler(BaseEventHandler):
    """Отправляет события клиентам через веб сокеты."""

    def __init__(self) -> None:
        self.clients: list[WebSocket] = []
        self.event_loop = asyncio.get_running_loop()

    async def connect(self, websocket: WebSocket) -> None:
        """Добавляет нового клиента."""
        await websocket.accept()
        self.clients.append(websocket)
        logger.info("New client, now {} clients", len(self.clients))

    def disconnect(self, websocket: WebSocket) -> None:
        """Отключает клиента от комнаты."""
        if websocket in self.clients:
            self.clients.remove(websocket)
        logger.info("Client disconnect, now {} clients", len(self.clients))

    def push(self, event: Event) -> None:
        """Отправляет событие клиентам."""
        event_data = EventData(
            event=event.event_type,
            player=player_to_data(event.player),
            data=event.data,
            game=game_to_data(event.game),
        )

        for connection in self.clients:
            try:
                self.event_loop.create_task(
                    connection.send_text(event_data.model_dump_json())
                )
            except Exception as e:
                logger.error(e)
