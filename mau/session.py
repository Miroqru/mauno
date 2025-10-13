"""Менеджер сессий.

Предоставляет высокоуровневый класс для работы с игровыми сессиями.
Обычно используется один менеджер сессий на платформу.
Он уже и будет руководить всеми играми и игроками.
"""

from typing import Generic, TypeVar

from loguru import logger

from mau.events import BaseEventHandler, GameEvents
from mau.game.game import MauGame
from mau.game.player import BaseUser, Player
from mau.game.player_manager import PlayerManager

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
        event_handler: Обработчик событий. Поставляется в игры для обработку
            всех происходящих событий.

    """

    __slots__ = ("_games", "_players", "_event_handler", "_active_players")

    def __init__(
        self,
        event_handler: _H,
    ) -> None:
        self._games: dict[str, MauGame] = {}
        self._active_players: dict[str, str] = {}
        self._event_handler = event_handler

    def player(self, user_id: str) -> Player | None:
        """Возвращает игрока напрямую из хранилища по ID пользователя."""
        game_id = self._active_players.get(user_id)
        if game_id is None:
            return None
        game = self._games.get(game_id)
        if game is None:
            self._active_players.pop(user_id)
            return None

        return game.pm.get(user_id)

    def room(self, room_id: str) -> MauGame | None:
        """Возвращает игру напрямую из хранилища по ID комнаты."""
        return self._games.get(room_id)

    def join(self, room_id: str, user: BaseUser) -> Player | None:
        """Присоединиться к игре.

        Записывает игрока в список активных игроков.
        Полезно для блокировки активных игроков, чтобы один игрок
        не мог участвовать сразу в нескольких играх.
        """
        active_game = self._active_players.get(user.id)
        if active_game is not None:
            raise ValueError("User already in game")

        game = self.room(room_id)
        if game is None:
            raise ValueError("game not found")
        self._active_players[user.id] = room_id
        player = game.join_player(user)
        if player is None:
            return None

        game.dispatch(player, GameEvents.SESSION_JOIN)
        return player

    def leave(
        self, player: Player, room_id: str | None = None
    ) -> Player | None:
        """Выход из игры.

        Дополнительно снимает блокировку активного игрока.
        Чтобы игрок мог принять участие в другой игре.
        """
        room_id = room_id or self._active_players.get(player.user_id)
        if room_id is None:
            raise ValueError("User not in game")

        self._active_players.pop(player.user_id)
        game = self.room(room_id)
        if game is None:
            return None

        game.leave_player(player)
        game.dispatch(player, GameEvents.SESSION_LEAVE)

    def create(
        self,
        room_id: str,
        owner: BaseUser,
        min_players: int = 2,
        max_players: int = 8,
    ) -> MauGame:
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
            min_players: Минимальное число игроков для начала игры.
            max_players: Максимальное число игроков в одной игре.
                Не рекомендуется изменять, поскольку карт может не хватить
                на всех игроков.

        """
        logger.info("User {} Create new game session in {}", owner, room_id)
        pm = PlayerManager(min_players, max_players)
        game = MauGame(pm, self._event_handler, room_id, owner)
        self._games[room_id] = game
        game.dispatch(game.owner, GameEvents.SESSION_START)
        return game

    def remove(self, room_id: str) -> None:
        """Полностью завершает игру в для указанной room ID.

        Должна выполняться после `game.end()`,
        поскольку очищает хранилище игроков.
        Удаляет игру из хранилища, отправляет событие `SESSION_END`.
        """
        logger.info("End session in room {}", room_id)
        game = self._games.pop(room_id)
        for pl in game.pm.iter():
            self._active_players.pop(pl.user_id)
        game.dispatch(game.owner, GameEvents.SESSION_END)
