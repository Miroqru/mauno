"""Колода карт для игры.

В колоде располагаются все карты для игры.
После эти карты могут перемещаться в руку игрока или обратно в колоду.
Также хранит информацию о текущей верхней карте колоды.
"""

from collections.abc import Iterator
from random import shuffle

from loguru import logger

from mau.card import BaseCard, CardColor, CardType


class Deck:
    """Колода карт.

    В колоде располагаются все карты для игры.
    Предоставляется методы для добавления, удаления и перемещения карт.
    """

    def __init__(self, cards: list[BaseCard] | None = None) -> None:
        self.cards: list[BaseCard] = cards or []
        self.used_cards: list[BaseCard] = []
        self._top: BaseCard | None = None

    @property
    def top(self) -> BaseCard:
        """Возвращает верхнюю карту из колоды."""
        if self._top is None:
            raise ValueError("Top card not be None, is deck fill?")
        return self._top

    def clear(self) -> None:
        """Очищает колоду карт."""
        self.cards.clear()
        self.used_cards.clear()
        self._top = None
        logger.info("Deck cleared")

    def shuffle(self) -> None:
        """Перемешивает карты в колоде.

        Обязательно перемешивайте карты в колоде как добавили их.
        """
        shuffle(self.cards)

    def prepared_used_cards(self) -> None:
        """Возвращает использованные карты в колоду."""
        self.cards.extend(self.used_cards)
        self.used_cards.clear()
        self.shuffle()

    def take(self, count: int = 1) -> Iterator:
        """Берёт одну карту из колоды.

        Используется чтобы дать участнику несколько карт.

        Args:
            count (int, optional): Сколько взять карт (одну).

        Yields:
            Iterator: Возвращает по одной карте из всех взятых.

        """
        if len(self.cards) < count:
            self.prepared_used_cards()
        if len(self.cards) < count:
            for card in self.cards:
                yield card

        for i in range(count):
            card = self.cards.pop()
            logger.debug("Take {} / {} card: {}", i, count, card)
            yield card

    def take_one(self) -> BaseCard:
        """Берёт одну карту из колоды.

        В тех случаях, когда нужно взять только одну карту.
        """
        logger.debug("Take one card from deck")
        return self.cards.pop()

    def count_until_cover(self) -> int:
        """Получает количество кард в колоде до подходящей."""
        for i, card in enumerate(reversed(self.cards)):
            if self.top.can_cover(card):
                return i + 1
        return 1

    def put(self, card: BaseCard) -> None:
        """Возвращает использованную карту в колоду."""
        if card.card_type in (CardType.TAKE_FOUR, CardType.CHOOSE_COLOR):
            card.color = CardColor.BLACK
        self.used_cards.append(card)

    def put_on_top(self, card: BaseCard) -> None:
        """Ложит карту на вершину стопки."""
        if self._top is None:
            self._top = card

        self.put(self._top)
        self._top = card
