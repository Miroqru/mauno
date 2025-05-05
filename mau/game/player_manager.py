"""Менеджер игроков в рамках одной игры."""

from collections import deque
from collections.abc import Iterable, Iterator
from random import shuffle

from mau.enums import GameEvents
from mau.game.player import Player
from mau.storage import BaseStorage


class PlayerManager:
    """Менеджер игроков.

    Позволяет взаимодействовать с игроками в рамках одной игры.
    """

    __slots__ = ("_storage", "_players", "winners", "losers", "_cp")

    def __init__(self, storage: BaseStorage) -> None:
        self._storage = storage
        self._cp = 0

        self._players: list[str] = []
        self.winners: list[str] = []
        self.losers: list[str] = []

    @property
    def current(self) -> Player:
        """Получает текущего игрока."""
        if len(self._players) == 0:
            raise ValueError("Game not started to get players")
        pl = self.get(self._players[self._cp % len(self._players)])
        if pl is None:
            raise ValueError("No players in game")
        return pl

    def get(self, user_id: str) -> Player:
        """Возвращает игрока из хранилища по его ID."""
        pl = self._storage.get(user_id)
        if pl is None:
            raise ValueError(f"Where player with ID {user_id}")
        return pl

    def get_or_none(self, user_id: str) -> Player | None:
        """Возвращает игрока из хранилища по его ID."""
        return self._storage.get(user_id)

    def iter(self, players: Iterable[str] | None = None) -> Iterator[Player]:
        """Проходится по всему списку игроков."""
        for pl in players or self._players:
            storage_player = self.get(pl)
            if storage_player is not None:
                yield storage_player

    def iter_others(self) -> Iterator[tuple[int, Player]]:
        """Возвращает индекс и ID всех игроков, кроме текущего."""
        yield from (
            (i, self.get(uid))
            for i, uid in enumerate(self._players)
            if i != self._cp
        )

    def add(self, player: Player) -> None:
        """Добавляет игрока в хранилище."""
        self._storage.add(player.user_id, player)
        self._players.append(player.user_id)

    def remove(self, player: Player) -> None:
        """Удаляет игрока из списка игроков."""
        if len(player.hand) == 0:
            self.winners.append(player.user_id)
        else:
            self.losers.append(player.user_id)
        self._players.remove(player.user_id)
        player.on_leave()

    def remove_players(self) -> None:
        """Удаляет всех игроков из хранилища, связанных с текущей игрой."""
        for pl in self.winners:
            self._storage.remove(pl)
        for pl in self.losers:
            self._storage.remove(pl)

    def start(self) -> None:
        """Подготавливает игроков к началу игры."""
        self.winners = []
        self.losers = []
        self._cp = 0
        shuffle(self._players)
        for player in self.iter(self._players):
            player.on_join()

    def end(self) -> None:
        """Подготавливает к завершению игры."""
        self.losers.extend(self._players)
        self._players = []

    def next(self, n: int = 1, reverse: bool = False) -> None:
        """Перемещает курсор игрока дальше."""
        if reverse:
            self._cp = (self._cp - n) % len(self._players)
        else:
            self._cp = (self._cp + n) % len(self._players)

    def set_cp(self, player: Player) -> None:
        """Устанавливает курсор текущего игрока на переданного."""
        for i, pl in enumerate(self._players):
            if player.user_id == pl:
                self._cp = i
                player.push_event(GameEvents.PLAYER_INTERVENED)
                return

    def rotate_cards(self, reverse: bool = False) -> None:
        """Меняет карты в руках для всех игроков."""
        hands = deque(player.hand for player in self.iter(self._players))
        hands.rotate(-1 if reverse else 1)
        for player, new_hand in zip(self.iter(self._players), hands):
            player.hand = new_hand

    def __len__(self) -> int:
        """Возвращает количество игроков в игре."""
        return len(self._players)
