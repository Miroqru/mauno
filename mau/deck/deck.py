"""Колода игровых карт.

В колоде располагаются все карты для игры.
После эти карты могут перемещаться в руку игрока или обратно в колоду.
"""

from collections.abc import Iterator
from random import randint, shuffle

from loguru import logger

from mau.deck import behavior
from mau.deck.behavior import CardBehavior
from mau.deck.card import MauCard
from mau.enums import CardColor


def deck_colors(cards: list[MauCard]) -> list[CardColor]:
    """Возвращает все использованные цвета в колоде, исключая дикие карты."""
    res: list[CardColor] = []
    for card in cards:
        if card.color not in res:
            res.append(card.color)
    return sorted(res)


# TODO: Внедрить прочие поведения
def _random_behavior() -> CardBehavior:
    return CardBehavior("random", 0, use=[behavior.log], cover=[])


def random_card() -> MauCard:
    """Отдаёт случайную карту."""
    value = randint(0, 9)
    behavior = _random_behavior()
    return MauCard(CardColor(randint(0, 7)), value, value, behavior)


class Deck:
    """Колода карт.

    В колоде располагаются все карты для игры.
    Карты из колоды попадают в руку игроков, а после использования
    возвращаются в колоду.
    Предоставляется методы для добавления, удаления и перемещения карт.
    """

    __slots__ = ("cards", "used_cards", "_top", "_colors", "_wild_color")

    def __init__(self, cards: list[MauCard] | None = None) -> None:
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
            self._colors.remove(self.wild_color)
        return self._colors

    @property
    def wild_color(self) -> CardColor:
        """Получает дикий цвет для колоды."""
        if self._wild_color is None:
            raise ValueError("Wild color can`t be None")
        return self._wild_color

    # TODO: Можно оповещать о событии для смены дикого цвета
    def set_wild(self, color: CardColor) -> None:
        """Устанавливает цвет дикой карты."""
        logger.info("Set wild color to {}", color)
        self._wild_color = color

    @property
    def top(self) -> MauCard:
        """Возвращает верхнюю карту из колоды."""
        if self._top is None:
            self._top = self._get_top_card()
        return self._top

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
            if card.color != self.wild_color:
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
            card = self.cards.pop(0)
            logger.debug("Take {} / {} card: {}", i, count, card)
            yield card

    def count_until_cover(self) -> int:
        """Получает количество кард в колоде до покрывающей верную."""
        for i, card in enumerate(self.cards):
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

    def __init__(self) -> None:
        super().__init__(None)
        self._colors = [CardColor(x) for x in range(8)]

    def _get_top_card(self) -> MauCard:
        """Устанавливает подходящую верную карту колоды."""
        while True:
            card = random_card()
            if card.color != self.wild_color:
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
