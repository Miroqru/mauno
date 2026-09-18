"""Менеджер сессий.

Предоставляет высокоуровневый класс для работы с игровыми сессиями.
Обычно используется один менеджер сессий на платформу.
Он уже и будет руководить всеми играми и игроками.
"""

from collections.abc import Mapping

from loguru import logger

from mau.events import EventHandler, GameEvents
from mau.game.game import MauGame
from mau.game.player import Player, PlayerID
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

    def __init__(self, event_handler: H) -> None:
        self._games: dict[RoomID, MauGame] = {}
        self._players: dict[str, RoomID] = {}
        self._event_handler = event_handler

    # Получение данных
    # ================

    @property
    def event_handler(self) -> H:
        """Возвращает привязанный обработчик событий."""
        return self._event_handler

    @property
    def rooms(self) -> Mapping[RoomID, MauGame]:
        """Возвращает словарь всех активных игр с привязкой к комнатам."""
        return self._games

    def room(self, room_id: RoomID) -> MauGame | None:
        """Возвращает экземпляр игры по ID комнаты из хранилища."""
        return self._games.get(room_id)

    def player(self, player_id: PlayerID) -> Player | None:
        """Возвращает игрока по его ID.

        Ищет среди активных игроков, а после обращается к менеджеру
        игроков в указанной игре.

        Автоматически очищает несуществующие игры.
        Если такого игрока не будет в игре - вернёт исключение.
        В любом другом случае вернёт либо игрока. либо None.
        """
        room_id = self._players.get(player_id)
        if room_id is None:
            return None

        game = self._games.get(room_id)
        if game is None:
            self._players.pop(player_id)
            return None

        return game.pm.get(player_id)

    # Высокоуровневое управление
    # ==========================

    def create(
        self,
        room_id: str,
        owner_id: PlayerID,
        owner_name: str,
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
            owner_id: Идентификатор владельца комнаты, станет первым игроком.
            owner_name: Имя владельца комнаты, станет первым игроком для игры.
            min_players: Минимальное число игроков для начала игры.
            max_players: Максимальное число игроков в одной игре.
                Не рекомендуется изменять, поскольку карт может не хватить
                на всех игроков.

        """
        logger.info("User {} Create new game session in {}", owner_name, room_id)
        pm = PlayerManager(min_players, max_players)
        game = MauGame(pm, self._event_handler, room_id, owner_id, owner_name)
        self._games[room_id] = game
        self._players[owner_id] = room_id
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

    def join(self, room_id: RoomID, player_id: PlayerID, name: str) -> Player:
        """Присоединиться к игре.

        Записывает игрока в список активных игроков.
        Полезно для блокировки активных игроков, чтобы один игрок
        не мог участвовать сразу в нескольких играх.

        Если не удалось присоединиться к игре, возвращает ошибку.
        """
        active_game = self._players.get(player_id)
        if active_game is not None:
            raise ValueError("User already in game")

        game = self.room(room_id)
        if game is None:
            raise ValueError("game not found")

        self._players[player_id] = room_id
        player = game.join_player(player_id, name)
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
