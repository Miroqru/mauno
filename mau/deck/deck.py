"""Колода игровых карт.

В колоде располагаются все карты для игры.
После эти карты могут перемещаться в руку игрока или обратно в колоду.
"""

from collections.abc import Iterator
from random import choice, randint, shuffle
from typing import TYPE_CHECKING

from loguru import logger

from mau.deck import behavior
from mau.deck.behavior import BaseWildBehavior
from mau.deck.card import MauCard
from mau.enums import CardColor

if TYPE_CHECKING:
    from mau.game.game import MauGame


def deck_colors(cards: list[MauCard]) -> list[CardColor]:
    """Возвращает все использованные цвета в колоде, исключая дикие карты."""
    res = []
    for card in cards:
        if isinstance(card.behavior, BaseWildBehavior):
            continue

        if card.color not in res:
            res.append(card.color)
    return sorted(res)


# TODO: Плохо выглядит, устранить
_BEHAVIORS = [
    behavior.NumberBehavior(),
    behavior.ReverseBehavior(),
    behavior.TurnBehavior(),
    behavior.TakeBehavior(),
    behavior.WildTakeBehavior(),
    behavior.WildColorBehavior(),
    behavior.TwistBehavior(),
    behavior.RotateBehavior(),
]

_COLORS = [
    CardColor(0),
    CardColor(1),
    CardColor(2),
    CardColor(3),
    CardColor(4),
    CardColor(5),
    CardColor(6),
    CardColor(7),
]


def random_card() -> MauCard:
    """Отдаёт случайную карту."""
    value = randint(0, 9)
    behavior = choice(_BEHAVIORS)
    cost = behavior.cost or value

    return MauCard(CardColor(randint(0, 7)), value, cost, behavior)


class Deck:
    """Колода карт.

    В колоде располагаются все карты для игры.
    Карты из колоды попадают в руку игроков, а после использования
    возвращаются в колоду.
    Предоставляется методы для добавления, удаления и перемещения карт.
    """

    __slots__ = (
        "_game",
        "cards",
        "used_cards",
        "_top",
        "_colors",
        "_wild_color",
    )

    def __init__(
        self, game: "MauGame", cards: list[MauCard] | None = None
    ) -> None:
        self._game = game
        self.cards: list[MauCard] = cards or []
        self.used_cards: list[MauCard] = []
        self._top: MauCard | None = None
        self._colors: list[CardColor] | None = None
        self._wild_color: CardColor | None = None

    @property
    def colors(self) -> list[CardColor]:
        """Получает список всех используемых цветов в колоде."""
        if self._colors is None:
            self._colors = deck_colors(self.cards)
        return self._colors

    @property
    def wild_color(self) -> CardColor:
        """Получает дикий цвет для колоды."""
        if self._wild_color is None:
            self._wild_color = self._get_wild_color()
        return self._wild_color

    @property
    def top(self) -> MauCard:
        """Возвращает верхнюю карту из колоды."""
        if self._top is None:
            self._top = self._get_top_card()
        return self._top

    def _get_wild_color(self) -> CardColor:
        """Устанавливает основной цвет для диких карт."""
        if self._game.rules.special_wild.status:
            return choice(self.colors)

        return CardColor.BLACK

    def shuffle(self) -> None:
        """Перемешивает доступные карты в колоде.

        Обязательно перемешивайте карты до начала игры.
        """
        logger.debug("Shuffle deck")
        shuffle(self.cards)

    def clear(self) -> None:
        """Очищает колоду карт."""
        logger.debug("Clear deck")
        self.cards = []
        self.used_cards = []
        self._top = None

    def _get_top_card(self) -> MauCard:
        """Устанавливает подходящую верную карту колоды."""
        for i, card in enumerate(self.cards):
            if not isinstance(card.behavior, BaseWildBehavior):
                return self.cards.pop(i)
        raise ValueError("No suitable card for deck top")

    def take(self, count: int = 1) -> Iterator[MauCard]:
        """Берёт несколько карт из колоды.

        Используется чтобы дать участнику несколько карт.
        """
        if len(self.cards) < count:
            self._prepared_used_cards()

        if len(self.cards) < count:
            raise ValueError("Not enough cards to take")

        for i in range(count):
            card = self.cards.pop()
            logger.debug("Take {} / {} card: {}", i, count, card)
            yield card

    def count_until_cover(self) -> int:
        """Получает количество кард в колоде до покрывающей верную."""
        for i, card in enumerate(reversed(self.cards)):
            if self.top.can_cover(card, self.wild_color):
                return i + 1
        return 1

    def _prepared_used_cards(self) -> None:
        """Возвращает использованные карты в колоду."""
        self.cards.extend(self.used_cards)
        self.used_cards = []
        self.shuffle()

    def put(self, card: MauCard) -> None:
        """Возвращает использованную карту в колоду."""
        card.prepare_used(self._game)
        self.used_cards.append(card)

    def put_top(self, card: MauCard) -> None:
        """Ложит карту на вершину стопки."""
        if self._top is None:
            self._top = card
            return

        self.put(self._top)
        self._top = card


class RandomDeck(Deck):
    """Колода случайных карт."""

    @property
    def colors(self) -> list[CardColor]:
        """Получает список всех используемых цветов в колоде."""
        return _COLORS

    def _get_top_card(self) -> MauCard:
        """Устанавливает подходящую верную карту колоды."""
        while True:
            card = random_card()
            if not isinstance(card.behavior, BaseWildBehavior):
                return card

    def take(self, count: int = 1) -> Iterator[MauCard]:
        """Берёт несколько карт из колоды.

        Используется чтобы дать участнику несколько карт.
        """
        for i in range(count):
            card = random_card()
            logger.debug("Take {} / {} card: {}", i, count, card)
            yield card

    def count_until_cover(self) -> int:
        """Получает количество кард в колоде до покрывающей верную."""
        return 1

    def put(self, card: MauCard) -> None:
        """Возвращает использованную карту в колоду."""
        logger.debug("Put {}", card)

    def put_top(self, card: MauCard) -> None:
        """Ложит карту на вершину стопки."""
        self._top = card
