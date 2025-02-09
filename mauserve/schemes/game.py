"""Схемы, используемые во время игры."""

from pydantic import BaseModel


class PlayerDta(BaseModel):
    pass


class GameData(BaseModel):
    owner_id: str
    players: str
