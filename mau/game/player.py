"""Представляет игроков, связанных с текущей игровой сессией."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, TypeVar

from loguru import logger

from mau.deck.card import CardColor
from mau.enums import GameState
from mau.events import EventType, GameEvent
from mau.rules import GameRules

if TYPE_CHECKING:
    from mau.deck.card import MauCard
    from mau.game.game import MauGame


_E = TypeVar("_E")
PlayerID = str


@dataclass(frozen=True, slots=True)
class SortedCards:
    """Распределяет карты на: покрывающие и не покрывающие."""

    cover: list[tuple[int, "MauCard"]]
    uncover: list[tuple[int, "MauCard"]]


class Player:
    """Игрок для сессии Mau.

    Каждый игрок привязывается к конкретной игровой сессии.
    Реализует команды для взаимодействия игрока с текущей сессией.
    """

    __slots__ = ("_game", "_hand", "_id", "_user_name")

    def __init__(self, game: "MauGame", player_id: PlayerID, user_name: str) -> None:
        self._hand: list[MauCard] = []
        self._game: MauGame = game
        self._id = player_id
        self._user_name = user_name

    @property
    def game(self) -> "MauGame":
        """Возвращает привязанную к игроку игру."""
        return self._game

    @property
    def hand(self) -> "list[MauCard]":
        """Возвращает карты пользователя."""
        return self._hand

    @property
    def id(self) -> PlayerID:
        """Возвращает внешний уникальный идентификатор игрока."""
        return self._id

    @property
    def name(self) -> str:
        """Возвращает строковое имя игрока."""
        return self._user_name

    @property
    def can_play(self) -> bool:
        """Может ли текущий игрок совершать ход."""
        return self._game.can_play(self)

    @property
    def is_owner(self) -> bool:
        """Является ли текущий игрок владельцем комнаты."""
        return self._game.is_owner(self)

    def is_bluffing(self) -> bool:
        """Проверяет блефует ли игрок, когда выкидывает дикую карту."""
        for card in self.cover_cards().cover:
            if card[1].color == self._game.deck.top.color:
                return True
        return False

    def count_cost(self) -> int:
        """Считает полную ценность руки пользователя."""
        return sum(c.cost for c in self._hand)

    def dispatch(self, event_type: EventType, data: _E) -> GameEvent[_E]:
        """Отправляет событие в журнал.

        Автоматически подставляет игрока и игру.
        Также можно напрямую вызвать метод или через класс игры.
        """
        e = GameEvent(
            game=self._game, player_id=self.id, event_type=event_type, data=data
        )
        self._game.event_handler.dispatch(e)
        return e

    def set_hand(self, cards: "list[MauCard]") -> None:
        """Выдаёт карты пользователя.

        Внешний метод для взаимодействия с рукой пользователя.
        """
        logger.debug("Set {} card for player {}", len(cards), self.id)
        self._hand = cards

    def take_cards(self) -> None:
        """Игрок берёт заданное количество карт согласно счётчику."""
        take_counter = self._game.take_counter or 1
        logger.debug("{} Draw {} cards", self._user_name, take_counter)

        for card in self._game.deck.take(take_counter):
            self._hand.append(card)
        self._game.take_counter = 0
        self.dispatch(EventType.PLAYER_TAKE, take_counter)
        self._game.set_state(GameState.TAKE)

        if (
            self._game.rules.status(GameRules.auto_skip)
            and len(self.cover_cards().cover) == 0
        ):
            self._game.next_turn()

    def cover_cards(self) -> SortedCards:
        """Возвращает отсортированный список карт из руки пользователя.

        Карты делятся на те, которыми он может покрыть и которыми не может
        покрыть текущую верхнюю карту.
        """
        top = self._game.deck.top
        logger.debug("Last card was {}", top)
        # Если мы сейчас в состоянии выбора цвета, револьвера. обмена руками
        # то нам сейчас карты нне очень важны
        if not self.can_play or self._game.state not in (
            GameState.NEXT,
            GameState.CONTINUE,
            GameState.TAKE,
        ):
            return SortedCards([], [(i, card) for i, card in enumerate(self._hand)])

        cover: list[tuple[int, MauCard]] = []
        uncover: list[tuple[int, MauCard]] = []
        for i, card in enumerate(self._hand):
            if self._game.can_cover(self, card):
                cover.append((i, card))
            else:
                uncover.append((i, card))

        return SortedCards(
            cover=sorted(cover, key=lambda c: c[1].cost, reverse=True),
            uncover=sorted(uncover, key=lambda c: c[1].cost, reverse=True),
        )

    def on_join(self) -> None:
        """Берёт начальный набор карт для игры."""
        logger.debug("{} Draw first hand for player", self._user_name)
        take_cards = self._game.settings.start_cards

        self._hand = list(self._game.deck.take(take_cards))
        self.dispatch(EventType.PLAYER_TAKE, take_cards)

    def on_leave(self) -> None:
        """Действия игрока при выходе из игры."""
        logger.debug("{} Leave from game", self._user_name)
        for card in self._hand:
            self._game.deck.put(card)
        self._hand = []

    def twist_hand(self, other_player: Self) -> None:
        """Меняет местами руки для двух игроков."""
        logger.info("Switch hand between {} and {}", self, other_player)
        player_hand = self._hand.copy()
        self._hand = other_player.hand[:]
        other_player.set_hand(player_hand)
        self.dispatch(EventType.GAME_SELECT_PLAYER, other_player.id)
        self.end_turn()

    def check_bluff(self) -> None:
        """Проверка предыдущего игрока на блеф.

        По правилам, если прошлый игрок блефовал, то он берёт 4 карты.
        Если же игрок не блефовал, текущий игрок берёт уже 6 карт.
        """
        logger.info("{} call bluff {}", self, self._game.bluff_state)
        if self._game.bluff_state is None or not self._game.bluff_state[1]:
            self._game.take_counter += 2
            self.take_cards()
        else:
            bluff_player = self._game.pm.get(self._game.bluff_state[0])
            bluff_player.take_cards()
        self.dispatch(EventType.PLAYER_BLUFF, None)
        self.end_turn()

    def end_turn(self) -> None:
        """Игрок завершает текущий ход."""
        if len(self._hand) == 1:
            self.dispatch(EventType.PLAYER_MAU, None)

        elif len(self._hand) == 0:
            self._game.leave_player(self)

        self._game.next_turn()

    def choose_color(self, color: CardColor) -> None:
        """Устанавливаем цвет для последней карты."""
        self._game.deck.top.color = color
        self.dispatch(EventType.GAME_SELECT_COLOR, color)
        self.end_turn()

    def __str__(self) -> str:
        """Представление игрока в строковом виде."""
        return str(self._user_name)

    def __eq__(self, other_player: object) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        if isinstance(other_player, Player):
            return self._id == other_player._id
        if isinstance(other_player, str):
            return self._id == other_player
        return NotImplemented

    def __ne__(self, other_player: object) -> bool:
        """Проверяет что игроки не совпадают."""
        if isinstance(other_player, Player):
            return self._id != other_player._id
        if isinstance(other_player, str):
            return self._id != other_player
        return NotImplemented


PlayerOrID = Player | PlayerID
"""Позволяет передавать игрока или его идентификатор.

Если передать идентификатор, метод сам получить по нему игрока.
"""
