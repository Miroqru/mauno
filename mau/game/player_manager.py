"""Менеджер игроков в рамках одной игры."""

from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import IntEnum
from random import shuffle

from mau.events import EventType
from mau.game.player import Player
from mau.types import PlayerID


class GameReverse(IntEnum):
    """Направление ходов в игре."""

    NEXT = 1
    BACK = 2
    STOP = 3


class ResultType(IntEnum):
    """Результат игры."""

    WINNER = 0
    DRAW = 1
    LOOSER = 2


@dataclass(slots=True, frozen=True)
class GameResult:
    """Результат игры для игрока."""

    winner: ResultType
    score: int


class PlayerManager:
    """Менеджер игроков.

    Позволяет взаимодействовать с игроками в рамках одной игры.
    """

    __slots__ = (
        "_cp",
        "_players",
        "_storage",
        "max_players",
        "min_players",
        "player_cost",
        "results",
        "reverse",
    )

    def __init__(self, min_players: int = 2, max_players: int = 6) -> None:
        self._storage: dict[PlayerID, Player] = {}
        self.min_players = min_players
        self.max_players = max_players
        self._cp = 0
        self.reverse = GameReverse.NEXT
        self._players: list[PlayerID] = []
        self.results: dict[PlayerID, GameResult] = {}
        self.player_cost: dict[PlayerID, int] = {}

    def cur(self, offset: int = 0) -> Player:
        """ПОлучает игрока по курсору со сдвигом."""
        if len(self._players) == 0:
            raise ValueError("Game not started to get players")

        cur = (self._cp + offset) % len(self._players)
        return self.get(self._players[cur])

    def get(self, player_id: PlayerID) -> Player:
        """Возвращает игрока из хранилища по его ID."""
        pl = self._storage.get(player_id)
        if pl is None:
            raise ValueError(f"Where player with ID {player_id}")
        return pl

    def get_or_none(self, player_id: PlayerID) -> Player | None:
        """Возвращает игрока из хранилища по его ID."""
        return self._storage.get(player_id)

    def iter(self, players: Iterable[str] | None = None) -> Iterator[Player]:
        """Проходится по всему списку игроков."""
        for pl in players or self._players:
            storage_player = self.get_or_none(pl)
            if storage_player is not None:
                yield storage_player

    def iter_others(self) -> Iterator[tuple[int, Player]]:
        """Возвращает индекс и ID всех игроков, кроме текущего."""
        yield from (
            (i, self.get(uid)) for i, uid in enumerate(self._players) if i != self._cp
        )

    def add(self, player: Player) -> None:
        """Добавляет игрока в хранилище.

        Вернёт исключение, если не получилось добавить игрока.
        """
        self._storage[player.id] = player
        self._players.append(player.id)

    def remove(self, player_id: PlayerID) -> Player:
        """Удаляет игрока из хранилища."""
        return self._storage.pop(player_id)

    def join(self, player: Player) -> None:
        """Позволяет игроку зайти в сессию."""
        if len(self._players) >= self.max_players:
            raise ValueError("Too man players in game")

        if player.id in self.results:
            raise ValueError("Player double join")

        self.add(player)

    def leave(self, player: Player, result: ResultType) -> None:
        """Игрок покидает игру при выигрыше или поражении."""
        self._players.remove(player.id)
        self.results[player.id] = GameResult(result, player.count_cost())

    def start(self) -> None:
        """Подготавливает игроков к началу новой игры.

        Вернёт исключение, если игроков недостаточно для игры.
        """
        if len(self._players) < self.min_players:
            raise ValueError("You need more players to start game")

        self.results = {}
        self._cp = 0
        shuffle(self._players)
        for player in self.iter(self._players):
            player.on_join()

    def end(self) -> None:
        """Подготавливает список игроков к завершению игры."""
        for pl in self.iter():
            self.results[pl.id] = GameResult(ResultType.LOOSER, pl.count_cost())
        self._players = []

    def set_reverse(self, reverse: GameReverse | None = None) -> None:
        """Устанавливает новое значение порядка ходов в игре."""
        if reverse is not None:
            self.reverse = reverse
        elif self.reverse == GameReverse.NEXT:
            self.reverse = GameReverse.BACK
        else:
            self.reverse = GameReverse.NEXT

    def next(self, n: int = 1) -> None:
        """Перемещает курсор игрока дальше."""
        if self.reverse == GameReverse.NEXT:
            self._cp = (self._cp + n) % len(self._players)

        elif self.reverse == GameReverse.BACK:
            self._cp = (self._cp - n) % len(self._players)

    def set_cp(self, player: Player) -> None:
        """Устанавливает курсор текущего игрока на переданного."""
        index = self._players.index(player.id)
        self._cp = index
        player.dispatch(EventType.PLAYER_INTERVENED, None)

    def rotate_cards(self) -> None:
        """Меняет карты в руках для всех игроков."""
        hands = deque(player.hand for player in self.iter(self._players))
        hands.rotate(1 if self.reverse == GameReverse.NEXT else -1)
        for player, new_hand in zip(self.iter(self._players), hands, strict=False):
            player.set_hand(new_hand)

    def __len__(self) -> int:
        """Возвращает количество игроков в игре."""
        return len(self._players)
