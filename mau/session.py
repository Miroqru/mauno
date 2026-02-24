"""Менеджер сессий.

Предоставляет высокоуровневый класс для работы с игровыми сессиями.
Обычно используется один менеджер сессий на платформу.
Он уже и будет руководить всеми играми и игроками.
"""

from typing import Generic, TypeVar

from loguru import logger

from mau.enums import GameEvents
from mau.events import BaseEventHandler, DebugEventHandler
from mau.game.game import MauGame
from mau.game.player import BaseUser, Player
from mau.game.player_manager import PlayerManager
from mau.storage import BaseStorage, MemoryStorage

_H = TypeVar("_H", bound=BaseEventHandler)


class SessionManager(Generic[_H]):
    """Менеджер сессий.

    Высокоуровневый класс для управления сессиями и игроками.
    Предоставляет высокоуровневые методы для создания и удаления игр.
    Привязывается к конкретному типу игр и хранилищу.

    Args:
        game_storage: Хранилище для игр. По умолчания в оперативной памяти.
            Каждая созданная игра связывается с идентификатором `room_id`.
            Таким образом в одном чате может находиться только одна комната.
        player_storage: Хранилище для игроков.
            По умолчанию в оперативной памяти.
            Каждый игрок может находиться только в одной игре (комнате).
        event_handler: Обработчик событий. Поставляется в игры для обработку
            всех происходящих событий.

    """

    __slots__ = ("_games", "_players", "_event_handler")

    def __init__(
        self,
        game_storage: BaseStorage | None = None,
        player_storage: BaseStorage | None = None,
        event_handler: _H | None = None,
    ) -> None:
        self._games: BaseStorage[MauGame] = game_storage or MemoryStorage()
        self._players: BaseStorage[Player] = player_storage or MemoryStorage()
        self._event_handler = event_handler or DebugEventHandler()

    def set_handler(self, handler: _H) -> None:
        """Устанавливает новый обработчик событий."""
        self._event_handler = handler

    def player(self, user_id: str) -> Player | None:
        """Возвращает игрока напрямую из хранилища по ID пользователя."""
        return self._players.get(user_id)

    def room(self, room_id: str) -> MauGame | None:
        """Возвращает игру напрямую из хранилища по ID комнаты."""
        return self._games.get(room_id)

    def create(self, room_id: str, owner: BaseUser, min_players: int = 2, max_players: int = 6) -> MauGame:
        """Создает новую игру.

        Автоматически поставляет менеджер игроков и обработчик событий
        для игры.
        Добавляет созданную игру в хранилище.
        Отправляет событие `SESSION_START` о начале новой сессии.

        Теперь можно добавить игроков через экземпляр игры, а после
        запустить игру.

        Args:
            room_id: к какой комнате будет привязана игра в хранилище.
            owner: Владелец комнаты, становится первым игроком.

        """
        logger.info("User {} Create new game session in {}", owner, room_id)
        pm = PlayerManager(self._players, min_players, max_players)
        game = MauGame(pm, self._event_handler, room_id, owner)
        self._games.add(room_id, game)
        game.dispatch(game.owner, GameEvents.SESSION_START)
        return game

    def remove(self, room_id: str) -> None:
        """Полностью завершает игру в для указанной room ID.

        Должна выполняться после `game.end()`,
        поскольку очищает хранилище игроков.
        Удаляет игру из хранилища, отправляет событие `SESSION_END`.
        """
        logger.info("End session in room {}", room_id)
        game: MauGame = self._games.remove(room_id)
        game.pm.remove_players()
        game.dispatch(game.owner, GameEvents.SESSION_END)
