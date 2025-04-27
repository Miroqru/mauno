"""Реализация хранилища пользователей."""

from mau.game.player import Player


class PlayerManager:
    """Хранилище пользователей.

    У каждого пользователя может быть только одна игра.
    """

    def __init__(self) -> None:
        self._players: dict[str, Player] = {}
