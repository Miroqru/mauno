"""Хранилище игровых сессий.

Занимается общей обработкой всех существующих сессий.
Отвечает за создание новых игр и привязыванию их к чату.
"""

from typing import Generic, TypeVar, cast

from loguru import logger

from mau.enums import GameEvents
from mau.events import BaseEventHandler, DebugEventHandler
from mau.game.game import UnoGame
from mau.game.player import BaseUser, Player
from mau.session.storage import BaseStorage, MemoryStorage

_H = TypeVar("_H", bound=BaseEventHandler)


class SessionManager(Generic[_H]):
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    __slots__ = ("_storage", "_event_handler")

    def __init__(
        self,
        storage: BaseStorage | None = None,
        event_handler: _H | None = None,
    ) -> None:
        self._storage: BaseStorage[UnoGame] = storage or MemoryStorage()
        self._event_handler = event_handler or cast(_H, DebugEventHandler())

    def set_handler(self, handler: _H) -> None:
        """Устанавливает обработчик событий."""
        self._event_handler = handler

    def join_game(self, room_id: str, user: BaseUser) -> None:
        """Добавляет нового игрока в игру."""
        game = self._storage.room_game(room_id)
        player = game.add_player(user)
        self._storage.add_player(room_id, player.user_id)
        game.push_event(player, GameEvents.SESSION_JOIN)

    def leave_game(self, player: Player) -> None:
        """Убирает игрока из игры."""
        player.game.remove_player(player)
        if player.game.started and len(player.game.players) <= 1:
            player.game.end()
        self._storage.remove_player(player.user_id)
        player.push_event(GameEvents.SESSION_LEAVE)

    def player_game(self, user_id: str) -> UnoGame:
        """Получает экземпляр игры, в которой находится игрок.

        Если такой игры нет - выплюнет исключение.
        """
        return self._storage.player_game(user_id)

    def room_game(self, room_id: str) -> UnoGame:
        """Возвращает игру по указанному ID комнаты."""
        return self._storage.room_game(room_id)

    def create(self, room_id: str, user: BaseUser) -> UnoGame:
        """Создает новую игру в чате."""
        logger.info("User {} Create new game session in {}", user, room_id)
        game = UnoGame(self._event_handler, room_id, user)
        self._storage.add_game(room_id, game)
        self._storage.add_player(room_id, user.id)
        game.push_event(game.owner, GameEvents.SESSION_START)
        return game

    def remove(self, room_id: str) -> None:
        """Полностью завершает игру в конкретном чате.

        Если вы хотите завершить текущий кон - воспользуйтесь методов
        `UnoGame.end()`.
        """
        logger.info("End session in room {}", room_id)
        game: UnoGame = self._storage.remove_game(room_id)
        self._storage.remove_room_players(room_id)
        game.push_event(game.owner, GameEvents.SESSION_END)
