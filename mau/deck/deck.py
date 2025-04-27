"""Колода игровых карт.

В колоде располагаются все карты для игры.
После эти карты могут перемещаться в руку игрока или обратно в колоду.
"""

from collections.abc import Iterator
from random import shuffle

from loguru import logger

from mau.deck.card import UnoCard
from mau.enums import CardColor


class Deck:
    """Колода карт.

    В колоде располагаются все карты для игры.
    Карты из колоды попадают в руку игроков, а после использования
    возвращаются в колоду.
    Предоставляется методы для добавления, удаления и перемещения карт.
    """

    __slots__ = ("cards", "used_cards", "_top")

    def __init__(self, cards: list[UnoCard] | None = None) -> None:
        self.cards: list[UnoCard] = cards or []
        self.used_cards: list[UnoCard] = []
        self._top: UnoCard | None = None

    @property
    def top(self) -> UnoCard:
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

    def _get_top_card(self) -> UnoCard:
        """Устанавливает подходящую верную карту колоды."""
        for i, card in enumerate(self.cards):
            if card.color != CardColor.BLACK:
                return self.cards.pop(i)
        raise ValueError("No suitable card for deck top")

    def take(self, count: int = 1) -> Iterator[UnoCard]:
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
            if self.top.can_cover(card):
                return i + 1
        return 1

    def _prepared_used_cards(self) -> None:
        """Возвращает использованные карты в колоду."""
        self.cards.extend(self.used_cards)
        self.used_cards = []
        self.shuffle()

    def put(self, card: UnoCard) -> None:
        """Возвращает использованную карту в колоду."""
        card.prepare_used()
        self.used_cards.append(card)

    def put_top(self, card: UnoCard) -> None:
        """Ложит карту на вершину стопки."""
        if self._top is None:
            self._top = card
            return

        self.put(self._top)
        self._top = card
