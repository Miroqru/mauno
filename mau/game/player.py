"""Представляет игроков, связанных с текущей игровой сессией."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from loguru import logger

from mau.enums import CardType, GameEvents, GameState
from mau.events import Event
from mau.game.shotgun import Shotgun

if TYPE_CHECKING:
    from mau.deck.card import UnoCard
    from mau.game.game import UnoGame


_MIN_SHOTGUN_TAKE_COUNTER = 3


# TODO: Отдельно добавить имя игрока, кроме упомянашки
@dataclass(frozen=True, slots=True)
class BaseUser:
    """Абстрактное представление пользователя.

    Представляет собой хранимую о пользователе информацию.
    Чтобы отвязать пользователя от конкретной реализации.
    """

    id: str
    name: str


@dataclass(frozen=True, slots=True)
class SortedCards:
    """Распределяет карты на: покрывающие и не покрывающие."""

    cover: list["UnoCard"]
    uncover: list["UnoCard"]


class Player:
    """Игрок для сессии Uno.

    Каждый игрок привязывается к конкретной игровой сессии.
    Реализует команды для взаимодействия игрока с текущей сессией.
    """

    def __init__(self, game: "UnoGame", user_id: str, user_name: str) -> None:
        self.hand: list[UnoCard] = []
        self.game: UnoGame = game
        self.user_id = user_id
        self._user_name = user_name
        self.shotgun = Shotgun()

    @property
    def name(self) -> str:
        """Возвращает имя игрока с упоминанием пользователя ядл бота."""
        return self._user_name

    @property
    def can_play(self) -> bool:
        """Имеет ли право хода текущий игрок."""
        return self.game.can_play(self.user_id)

    def is_bluffing(self) -> bool:
        """Проверяет блефует ли игрок, когда выкидывает дикую карту."""
        for card in self.cover_cards().cover:
            if card.color == self.game.deck.top.color:
                return True
        return False

    def push_event(self, event_type: GameEvents, data: str = "") -> None:
        """Отправляет событие в журнал.

        Автоматически подставляет игрока и игру.
        """
        self.game.event_handler.push(Event(self.game, self, event_type, data))

    def take_cards(self) -> None:
        """Игрок берёт заданное количество карт согласно счётчику."""
        take_counter = self.game.take_counter or 1
        logger.debug("{} Draw {} cards", self._user_name, take_counter)

        for card in self.game.deck.take(take_counter):
            self.hand.append(card)
        self.game.take_counter = 0
        self.push_event(GameEvents.PLAYER_TAKE, str(take_counter))
        self.game.set_state(GameState.TAKE)

        if (
            self.game.rules.auto_skip.status
            and len(self.cover_cards().cover) == 0
        ):
            self.game.next_turn()

    def cover_cards(self) -> SortedCards:
        """Возвращает отсортированный список карт из руки пользователя.

        Карты делятся на те, которыми он может покрыть и которыми не может
        покрыть текущую верхнюю карту.
        """
        top = self.game.deck.top
        logger.debug("Last card was {}", top)
        # Если мы сейчас в состоянии выбора цвета, револьвера. обмена руками
        # то нам сейчас карты нне очень важны
        # Если сейчас не ход игрока, то активных карт нету
        # Это для глупенького веб клиента будет полезно
        if (
            top.card_type == CardType.TAKE_FOUR
            and self.game.take_counter
            or self.game.state
            not in (GameState.NEXT, GameState.CONTINUE, GameState.TAKE)
            or not self.can_play
        ):
            return SortedCards([], self.hand)

        cover = []
        uncover = []
        for card, can_cover in top.iter_covering(self.hand):
            if (
                self.game.rules.intervention.status
                and card != top
                and self != self.game.player
            ):
                uncover.append(card)
                continue

            if not can_cover:
                uncover.append(card)
                continue

            if (
                top.card_type == CardType.TAKE
                and self.game.take_counter
                and card.card_type != CardType.TAKE
            ):
                uncover.append(card)
                continue

            cover.append(card)

        return SortedCards(
            cover=sorted(cover, key=lambda c: c.cost, reverse=True),
            uncover=sorted(uncover, key=lambda c: c.cost, reverse=True),
        )

    # TODO: Режим отладки
    def on_join(self) -> None:
        """Берёт начальный набор карт для игры."""
        self.shotgun.reset()
        logger.debug("{} Draw first hand for player", self._user_name)
        self.hand = list(self.game.deck.take(7))
        self.push_event(GameEvents.PLAYER_TAKE, "7")

    def on_leave(self) -> None:
        """Действия игрока при выходе из игры."""
        logger.debug("{} Leave from game", self._user_name)
        for card in self.hand:
            self.game.deck.put(card)
        self.hand = []

    def twist_hand(self, other_player: Self) -> None:
        """Меняет местами руки для двух игроков."""
        logger.info("Switch hand between {} and {}", self, other_player)
        player_hand = self.hand.copy()
        self.hand = other_player.hand.copy()
        other_player.hand = player_hand
        self.push_event(GameEvents.GAME_SELECT_PLAYER, other_player.user_id)
        self.game.next_turn()

    def shot(self) -> bool:
        """Выстрелить из револьвера."""
        if self.game.rules.single_shotgun.status:
            res = self.game.shotgun.shot()
            if res:
                self.game.shotgun.reset()
            return res
        return self.shotgun.shot()

    def call_bluff(self) -> None:
        """Проверка предыдущего игрока на блеф.

        По правилам, если прошлый игрок блефовал, то он берёт 4 карты.
        Если же игрок не блефовал, текущий игрок берёт уже 6 карт.
        """
        logger.info("{} call bluff {}", self, self.game.bluff_player)
        if self.game.bluff_player is None or not self.game.bluff_player[1]:
            self.game.take_counter += 2
            self.push_event(GameEvents.PLAYER_BLUFF)
            self.take_cards()
        else:
            self.push_event(GameEvents.PLAYER_BLUFF)
            self.game.bluff_player[0].take_cards()
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
            self.game.set_state(GameState.SHOTGUN)
            return

        logger.info("{} take cards", self)
        take_counter = self.game.take_counter
        self.take_cards()

        # Если пользователь выбрал взять карты, то он пропускает свой ход
        if (
            self.game.deck.top.card_type in (CardType.TAKE, CardType.TAKE_FOUR)
            and take_counter
        ):
            self.game.next_turn()

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
