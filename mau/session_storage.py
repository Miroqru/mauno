"""Хранилище игровых сессий."""

from abc import ABC, abstractmethod

from mau import exceptions
from mau.game import UnoGame


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
    def get_room(self, user_id: str) -> str:
        """Возвращает room_id для указанного игрока."""
        pass

    @abstractmethod
    def get_player_game(self, user_id: str) -> UnoGame:
        """Возвращает игру, в которой находится игрок."""
        pass

    @abstractmethod
    def add_game(self, room_id: str, game: UnoGame) -> None:
        """Добавляет новую игру в хранилище."""
        pass

    @abstractmethod
    def get_game(self, room_id: str) -> UnoGame:
        """Возвращает игру по указанному room_id."""
        pass

    @abstractmethod
    def remove_game(self, room_id: str) -> UnoGame:
        """Удаляет комнату из хранилища."""
        pass


class MemoryStorage(BaseStorage):
    """Хранилище сессий в памяти.

    Самые простой вид хранилища.
    Сохраняет состояние в оперативной памяти.
    Сессии будут очищены после перезапуска программы.

    У каждого игрока может быть только одна активная игра.
    """

    def __init__(self) -> None:
        self.games: dict[str, UnoGame] = {}
        self.user_to_room: dict[str, str] = {}

    def add_player(self, room_id: str, user_id: str) -> None:
        """Добавляет игрока в указанную комнату."""
        self.user_to_room[user_id] = room_id

    def remove_player(self, user_id: str) -> None:
        """Удаляет игрока из хранилища."""
        self.user_to_room.pop(user_id)

    def remove_room_players(self, room_id: str) -> None:
        """Удаляет пользователей, привязанных к комнате."""
        self.user_to_room = {
            user: room
            for user, room in self.user_to_room.items()
            if room != room_id
        }

    def get_room(self, user_id: str) -> str:
        """Возвращает room_id для указанного игрока."""
        try:
            return self.user_to_room[user_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def get_player_game(self, user_id: str) -> UnoGame:
        """Возвращает игру, в которой находится игрок."""
        try:
            room_id = self.user_to_room[user_id]
            return self.games[room_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def get_game(self, room_id: str) -> UnoGame:
        """Возвращает игру по room_id."""
        try:
            return self.games[room_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def add_game(self, room_id: str, game: UnoGame) -> None:
        """Добавляет новую игру в хранилище."""
        self.games[room_id] = game

    def remove_game(self, room_id: str) -> UnoGame:
        """Удаляет комнату из хранилища."""
        try:
            return self.games.pop(room_id)
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError
