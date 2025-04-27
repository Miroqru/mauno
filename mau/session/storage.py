"""Хранилище игровых сессий."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from mau import exceptions

if TYPE_CHECKING:
    from mau.game.game import UnoGame

# TODO: Может дженерики?


class BaseStorage(ABC):
    """Базовое хранилище сессий.

    Описывает интерфейс для работы с хранилищем сессий.
    Позволяет сохранять состояние игр в памяти.
    """

    @abstractmethod
    def add_player(self, room_id: str, user_id: str) -> None:
        """Добавляет игрока в указанную комнату."""
        pass

    @abstractmethod
    def remove_player(self, user_id: str) -> None:
        """Удаляет игрока из хранилища."""
        pass

    @abstractmethod
    def remove_room_players(self, room_id: str) -> None:
        """Удаляет пользователей, привязанных к комнате."""
        pass

    @abstractmethod
    def player_game(self, user_id: str) -> "UnoGame":
        """Возвращает игру, в которой находится игрок."""
        pass

    @abstractmethod
    def add_game(self, room_id: str, game: "UnoGame") -> None:
        """Добавляет новую игру в хранилище."""
        pass

    @abstractmethod
    def room_game(self, room_id: str) -> "UnoGame":
        """Возвращает игру по указанному id комнаты."""
        pass

    @abstractmethod
    def remove_game(self, room_id: str) -> "UnoGame":
        """Удаляет комнату из хранилища."""
        pass


class MemoryStorage(BaseStorage):
    """Хранилище сессий в памяти.

    Самые простой вид хранилища.
    Сохраняет состояние в оперативной памяти.
    Сессии будут очищены после перезапуска программы.

    У каждого игрока может быть только одна активная игра.
    """

    __slots__ = ("_games", "_user_room")

    def __init__(self) -> None:
        self._games: dict[str, UnoGame] = {}
        self._user_room: dict[str, str] = {}

    def add_player(self, room_id: str, user_id: str) -> None:
        """Добавляет игрока в указанную комнату."""
        self._user_room[user_id] = room_id

    def remove_player(self, user_id: str) -> None:
        """Удаляет игрока из хранилища."""
        self._user_room.pop(user_id)

    def remove_room_players(self, room_id: str) -> None:
        """Удаляет пользователей, привязанных к комнате."""
        self._user_room = {
            user: room
            for user, room in self._user_room.items()
            if room != room_id
        }

    def player_game(self, user_id: str) -> "UnoGame":
        """Возвращает игру, в которой находится игрок."""
        try:
            room_id = self._user_room[user_id]
            return self._games[room_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def room_game(self, room_id: str) -> "UnoGame":
        """Возвращает игру по ID комнаты."""
        try:
            return self._games[room_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def add_game(self, room_id: str, game: "UnoGame") -> None:
        """Добавляет новую игру в хранилище."""
        self._games[room_id] = game

    def remove_game(self, room_id: str) -> "UnoGame":
        """Удаляет комнату из хранилища."""
        try:
            return self._games.pop(room_id)
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError
