"""Представляет игроков, связанных с текущей игровой сессией."""

from dataclasses import dataclass
from random import randint
from typing import TYPE_CHECKING, NamedTuple, Self

from loguru import logger

from mau.card import (
    BaseCard,
    CardColor,
    NumberCard,
    ReverseCard,
    TakeCard,
    TakeFourCard,
    TurnCard,
)
from mau.enums import GameEvents, GameState
from mau.events import Event
from mau.exceptions import DeckEmptyError

if TYPE_CHECKING:
    from mau.game import UnoGame


# Дополнительные типы данных
# ==========================

_MIN_SHOTGUN_TAKE_COUNTER = 3


@dataclass(frozen=True)
class BaseUser:
    """Абстрактное представление пользователя.

    Представляет собой хранимую о пользователе информацию.
    Чтобы отвязать пользователя от конкретной реализации.
    """

    id: str
    name: str


class SortedCards(NamedTuple):
    """Распределяет карты на: покрывающие и не покрывающие."""

    cover: list[BaseCard]
    uncover: list[BaseCard]


class Player:
    """Игрок для сессии Uno.

    Каждый игрок привязывается к конкретной игровой сессии.
    Реализует команды для взаимодействия игрока с текущей сессией.
    """

    def __init__(self, game: "UnoGame", user_id: str, user_name: str) -> None:
        self.hand: list[BaseCard] = []
        self.game: UnoGame = game
        self.user_id = user_id
        self._user_name = user_name

        self.bluffing = False
        self.anti_cheat = 0

        self.shotgun_current = 0
        self.shotgun_lose = 0

    @property
    def name(self) -> str:
        """Возвращает имя игрока с упоминанием пользователя ядл бота."""
        return self._user_name

    @property
    def can_play(self) -> bool:
        """Имеет ли право хода текущий игрок."""
        return self.game.can_play(self.user_id)

    def push_event(self, event_type: GameEvents, data: str = "") -> None:
        """Отправляет событие в журнал.

        Автоматически подставляет игрока и игру.
        """
        self.game.event_handler.push(
            Event(self.game.room_id, self, event_type, data, self.game)
        )

    def take_first_hand(self) -> None:
        """Берёт начальный набор карт для игры."""
        self.shotgun_lose = randint(1, 8)
        if self.game.rules.debug_cards.status:
            logger.debug("{} Draw debug first hand for player", self._user_name)
            self.hand = [
                TakeFourCard(),
                TakeFourCard(),
            ]
            for x in (0, 1, 2, 3):
                self.hand.extend(
                    (
                        TakeCard(CardColor(x)),
                        TurnCard(CardColor(x), 1),
                        ReverseCard(CardColor(x)),
                        NumberCard(CardColor(x), 7),
                        NumberCard(CardColor(x), 2),
                        NumberCard(CardColor(x), 0),
                    )
                )
            return

        logger.debug("{} Draw first hand for player", self._user_name)
        try:
            self.hand = list(self.game.deck.take(7))
            self.push_event(GameEvents.PLAYER_TAKE, "7")
        except DeckEmptyError:
            for card in self.hand:
                self.game.deck.put(card)
            logger.warning("There not enough cards in deck for player")
            raise DeckEmptyError()

    def take_cards(self) -> None:
        """Игрок берёт заданное количество карт согласно счётчику."""
        take_counter = self.game.take_counter or 1
        logger.debug("{} Draw {} cards", self._user_name, take_counter)

        for card in self.game.deck.take(take_counter):
            self.hand.append(card)
        self.game.take_counter = 0
        self.push_event(GameEvents.PLAYER_TAKE, str(take_counter))
        self.game.take_flag = True

        if self.game.rules.auto_skip.status:
            cards = self.get_cover_cards()
            if len(cards.cover) == 0:
                self.game.next_turn()

    def _sort_hand_cards(self, top: BaseCard) -> SortedCards:
        cover = []
        uncover = []
        for card, can_cover in top.get_cover_cards(self.hand):
            if not can_cover:
                uncover.append(card)
                continue
            if (
                isinstance(top, TakeCard)
                and self.game.take_counter
                and not isinstance(card, TakeCard)
            ):
                uncover.append(card)
                continue

            cover.append(card)
            self.bluffing = (
                self.bluffing or card.color == self.game.deck.top.color
            )

        return SortedCards(sorted(cover), sorted(uncover))

    def _get_equal_cards(self, top: BaseCard) -> SortedCards:
        cover = []
        uncover = []
        for card in self.hand:
            if card != top:
                uncover.append(card)
                continue
            if (
                isinstance(top, TakeCard)
                and self.game.take_counter
                and not isinstance(card, TakeCard)
            ):
                uncover.append(card)
                continue

            cover.append(card)
            self.bluffing = (
                self.bluffing or card.color == self.game.deck.top.color
            )

        return SortedCards(sorted(cover), sorted(uncover))

    def get_cover_cards(self) -> SortedCards:
        """Возвращает отсортированный список карт из руки пользователя.

        Карты делятся на те, которыми он может покрыть и которыми не может
        покрыть текущую верхнюю карту.
        """
        top = self.game.deck.top
        logger.debug("Last card was {}", top)
        self.bluffing = False
        if isinstance(top, TakeFourCard) and self.game.take_counter:
            return SortedCards([], self.hand)

        # Если мы сейчас в состоянии выбора цвета, револьвера. обмена руками
        # то нам сейчас карты нне очень важны
        if self.game.state not in (GameState.NEXT, GameState.CONTINUE):
            return SortedCards([], self.hand)

        # Если сейчас не ход игрока, то активных карт нету
        # Это для глупенького веб клиента будет полезно
        if not self.can_play:
            return SortedCards([], self.hand)

        if self.game.rules.intervention.status and self.game.player != self:
            return self._get_equal_cards(top)
        return self._sort_hand_cards(top)

    # Обработка событий
    # =================

    def on_leave(self) -> None:
        """Действия игрока при выходе из игры."""
        logger.debug("{} Leave from game", self._user_name)
        # Если он последний игрок, подчищать за собой не приходится
        if len(self.game.players) == 1:
            return

        for card in self.hand:
            self.game.deck.put(card)
        self.hand.clear()

    def twist_hand(self, other_player: Self) -> None:
        """Меняет местами руки для двух игроков."""
        logger.info("Switch hand between {} and {}", self, other_player)
        player_hand = self.hand.copy()
        self.hand = other_player.hand.copy()
        other_player.hand = player_hand
        self.push_event(GameEvents.GAME_SELECT_PLAYER, other_player.user_id)
        self.game.next_turn()

    def shotgun(self) -> bool:
        """Выстрелить из револьвера."""
        if self.game.rules.single_shotgun.status:
            self.game.shotgun_current += 1
            is_fired = self.game.shotgun_current >= self.game.shotgun_lose
            if is_fired:
                self.game.shotgun_lose = randint(1, 8)
                self.game.shotgun_current = 0
            return is_fired
        self.shotgun_current += 1
        return self.shotgun_current >= self.shotgun_lose

    # Обработка игровых действий
    # ==========================

    def call_bluff(self) -> None:
        """Проверка предыдущего игрока на блеф.

        По правилам, если прошлый игрок блефовал, то он берёт 4 карты.
        Если же игрок не блефовал, текущий игрок берёт уже 6 карт.
        """
        logger.info("{} call bluff {}", self, self.game.bluff_player)
        bluff_player = self.game.bluff_player
        if bluff_player is not None and bluff_player.bluffing:
            self.push_event(
                GameEvents.PLAYER_BLUFF, f"true;{self.game.take_counter}"
            )
            bluff_player.take_cards()
        else:
            self.game.take_counter += 2
            self.push_event(
                GameEvents.PLAYER_BLUFF, f"false;{self.game.take_counter}"
            )
            self.take_cards()

        self.game.next_turn()

    def call_take_cards(self) -> None:
        """Действия игрока при взятии карты.

        В зависимости от правил, можно взять не одну карту, а сразу
        несколько.
        Если включен револьвер, то при взятии нескольких карт будет
        выбор:

        - Брать карты сейчас.
        - Выстрелить, чтобы взял следующий игрок.
        """
        if (
            self.game.rules.take_until_cover.status
            and self.game.take_counter == 0
        ):
            self.game.take_counter = self.game.deck.count_until_cover()

        if (
            self.game.take_counter > _MIN_SHOTGUN_TAKE_COUNTER
            and (
                self.game.rules.shotgun.status
                or self.game.rules.single_shotgun.status
            )
            and self.game.state != GameState.SHOTGUN
        ):
            self.game.state = GameState.SHOTGUN
            self.push_event(GameEvents.GAME_STATE, "shotgun")
            return

        logger.info("{} take cards", self)
        take_counter = self.game.take_counter
        self.take_cards()

        # Если пользователь выбрал взять карты, то он пропускает свой ход
        if (
            isinstance(self.game.deck.top, TakeCard | TakeFourCard)
            and take_counter
        ):
            self.game.next_turn()
        else:
            self.game.state = GameState.NEXT

    # Магические методы
    # =================

    def __repr__(self) -> str:
        """Представление игрока при отладке."""
        return repr(self._user_name)

    def __str__(self) -> str:
        """Представление игрока в строковом виде."""
        return str(self._user_name)

    def __eq__(self, other_player: object) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        if isinstance(other_player, Player):
            return self.user_id == other_player.user_id
        elif isinstance(other_player, str):
            return self.user_id == other_player
        return NotImplemented

    def __ne__(self, other_player: object) -> bool:
        """Проверяет что игроки не совпадают."""
        if isinstance(other_player, Player):
            return self.user_id != other_player.user_id
        elif isinstance(other_player, str):
            return self.user_id != other_player
        return NotImplemented
