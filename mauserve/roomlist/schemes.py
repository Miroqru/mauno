"""Схема списка комнат.

Используются при взаимодействии с комнатами
"""

from pydantic import BaseModel


class RoomMode(BaseModel):
    """Режим игры, изменяющий правила."""

    name: str
    desc: str | None
    status: bool


class RoomDataIn(BaseModel):
    """Изменяемые данные комнаты."""

    name: str | None = None
    private: bool | None = None
    room_password: str | None = None
    gems: int | None = None
    max_players: int | None = None
    min_players: int | None = None
