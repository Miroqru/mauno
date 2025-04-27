"""Хранилище игровых сессий.

Занимается общей обработкой всех существующих сессий.
Отвечает за создание новых игр и привязыванию их к чату.
"""

from typing import Generic, TypeVar, cast

from loguru import logger

from mau.enums import GameEvents
from mau.events import BaseEventHandler, DebugEventHandler
from mau.exceptions import NoGameInChatError
from mau.game.game import UnoGame
from mau.game.player import BaseUser, Player
from mau.game.player_manager import PlayerManager
from mau.storage import BaseStorage, MemoryStorage

_H = TypeVar("_H", bound=BaseEventHandler)


class SessionManager(Generic[_H]):
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    __slots__ = ("_games", "_players", "_event_handler")

    def __init__(
        self,
        game_storage: BaseStorage | None = None,
        player_storage: BaseStorage | None = None,
        event_handler: _H | None = None,
    ) -> None:
        self._games: BaseStorage[UnoGame] = game_storage or MemoryStorage()
        self._players: BaseStorage[Player] = player_storage or MemoryStorage()
        self._event_handler = event_handler or cast(_H, DebugEventHandler())

    def set_handler(self, handler: _H) -> None:
        """Устанавливает обработчик событий."""
        self._event_handler = handler

    # TODO: Время удалять
    def join_game(self, room_id: str, user: BaseUser) -> None:
        """Добавляет нового игрока в игру."""
        game = self._games.get(room_id)
        if game is None:
            raise NoGameInChatError from None
        player = game.join_player(user)
        game.push_event(player, GameEvents.SESSION_JOIN)

    def leave_game(self, player: Player) -> None:
        """Убирает игрока из игры."""
        player.game.remove_player(player)
        self._games.remove(player.user_id)
        player.push_event(GameEvents.SESSION_LEAVE)

    def player(self, user_id: str) -> Player | None:
        """Получает экземпляр игры, в которой находится игрок.

        Если такой игры нет - выплюнет исключение.
        """
        return self._players.get(user_id)

    def room(self, room_id: str) -> UnoGame:
        """Возвращает игру по указанному ID комнаты."""
        game = self._games.get(room_id)
        if game is None:
            raise NoGameInChatError from ValueError
        return game

    def create(self, room_id: str, user: BaseUser) -> UnoGame:
        """Создает новую игру в чате."""
        logger.info("User {} Create new game session in {}", user, room_id)
        pm = PlayerManager(self._players)
        game = UnoGame(pm, self._event_handler, room_id, user)
        self._games.add(room_id, game)
        self._players.add(user.id, game.owner)
        game.push_event(game.owner, GameEvents.SESSION_START)
        return game

    def remove(self, room_id: str) -> None:
        """Полностью завершает игру в конкретном чате.

        Если вы хотите завершить текущий кон - воспользуйтесь методов
        `UnoGame.end()`.
        """
        logger.info("End session in room {}", room_id)
        game: UnoGame = self._games.remove(room_id)
        game.pm.remove_players()
        game.push_event(game.owner, GameEvents.SESSION_END)
