"""Менеджер сессий.

Предоставляет высокоуровневый класс для работы с игровыми сессиями.
Обычно используется один менеджер сессий на платформу.
Он уже и будет руководить всеми играми и игроками.
"""

from collections.abc import Mapping

from loguru import logger

from mau.events import EventHandler, GameEvents
from mau.game.game import MauGame
from mau.game.player import BaseUser, Player
from mau.game.player_manager import PlayerManager

RoomID = str


class RoomManager[H: EventHandler]:
    """Менеджер комнат.

    Каждая игра здесь называется комнатой.
    Каждый игрок может участвовать только в одной активной игре.
    Задача менеджера - предоставлять высокоуровневый API для управления
    комнатами.
    Каждая комната привязывается к своему уникальному room_id.

    При инициализации передаётся обработчик событий, который будет
    реагировать на события, происходящие во всех комнатах.
    """

    __slots__ = ("_event_handler", "_games", "_players")

    def __init__(
        self,
        event_handler: H,
    ) -> None:
        self._games: dict[RoomID, MauGame] = {}
        self._players: dict[str, RoomID] = {}
        self._event_handler = event_handler

    # Получение данных
    # ================

    @property
    def rooms(self) -> Mapping[RoomID, MauGame]:
        """Возвращает словарь всех активных игр."""
        return self._games

    def room(self, room_id: RoomID) -> MauGame | None:
        """Возвращает по её ID из хранилища."""
        return self._games.get(room_id)

    def player(self, user_id: RoomID) -> Player | None:
        """Возвращает игрока по его ID.

        Ищет среди активных игроков, а после обращается к менеджеру
        игроков в указанной игре.

        Автоматически очищает несуществующие игры.
        Если такого игрока не будет в игре - вернёт исключение.
        В любом другом случае вернёт либо игрока. либо None.
        """
        room_id = self._players.get(user_id)
        if room_id is None:
            return None

        game = self._games.get(room_id)
        if game is None:
            self._players.pop(user_id)
            return None

        return game.pm.get(user_id)

    # Высокоуровневое управление
    # ==========================

    def create(
        self,
        room_id: str,
        owner: BaseUser,
        min_players: int = 2,
        max_players: int = 8,
    ) -> MauGame:
        """Создает новую игру.

        Автоматически поставляет менеджер игроков и обработчик событий.
        Отправляет событие `SESSION_START` о начале новой сессии.

        Все игрока добавляются через метод `join`.
        Чтобы начать игру, воспользуйтесь экземпляром игры.

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
        self._players[owner.id] = room_id
        game.owner.dispatch(GameEvents.SESSION_START, None)
        return game

    def remove(self, room_id: RoomID) -> None:
        """Полностью завершает игру.

        Очищает хранилище игроков.
        Должен запускаться после завершения игры.

        Удаляет игру из хранилища, отправляет событие `SESSION_END`.
        """
        logger.info("End session in room {}", room_id)
        game = self._games.pop(room_id)
        for pl in game.pm.iter():
            self._players.pop(pl.id)
        game.owner.dispatch(GameEvents.SESSION_END, None)

    def join(self, room_id: RoomID, user: BaseUser) -> Player:
        """Присоединиться к игре.

        Записывает игрока в список активных игроков.
        Полезно для блокировки активных игроков, чтобы один игрок
        не мог участвовать сразу в нескольких играх.

        Если не удалось присоединиться к игре, возвращает ошибку.
        """
        active_game = self._players.get(user.id)
        if active_game is not None:
            raise ValueError("User already in game")

        game = self.room(room_id)
        if game is None:
            raise ValueError("game not found")

        self._players[user.id] = room_id
        player = game.join_player(user)
        if player is None:
            raise ValueError("Failed to join game")

        player.dispatch(GameEvents.SESSION_JOIN, None)
        return player

    def leave(self, player: Player, room_id: RoomID | None = None) -> None:
        """Выход из игры.

        Используется игрок хочет полностью покинуть игру.
        К примеру чтобы досрочно выйти ищ игры.
        Или после того как игра завершилась, чтобы зайти в другую игру.

        Можно напрямую указать комнату, из которой нужен выйти.
        Иначе она будет получена из контекста.
        """
        room_id = room_id or self._players.get(player.id)
        if room_id is None:
            raise ValueError("User not in game")

        self._players.pop(player.id)
        game = self.room(room_id)
        if game is None:
            return

        game.leave_player(player)
        player.dispatch(GameEvents.SESSION_LEAVE, None)
