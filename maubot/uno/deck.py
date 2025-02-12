"""Колода карт для игры.

В колоде располагаются все карты для игры.
После эти карты могут перемещаться в руку игрока или обратно в колоду.
Также хранит информацию о текущей верхней карте колоды.
"""

from collections.abc import Iterator
from random import shuffle

from loguru import logger

from maubot.uno.card import (
    BaseCard,
    CardColor,
    ChooseColorCard,
    NumberCard,
    ReverseCard,
    TakeCard,
    TakeFourCard,
    TurnCard,
)


class Deck:
    """Колода карт.

    В колоде располагаются все карты для игры.
    Предоставляется методы для добавления, удаления и перемещения карт.
    """

    def __init__(self) -> None:
        self.cards: list[BaseCard] = []
        self.used_cards: list[BaseCard] = []
        self.top: BaseCard | None = None

    # Работа с целой колодой
    # ======================

    def clear(self) -> None:
        """Очищает колоду карт."""
        self.cards.clear()
        self.used_cards.clear()
        self.top = None
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

    # Работа с картами
    # ================

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
        self.used_cards.append(card)

    # Работа с верхней картой
    # =======================

    def put_on_top(self, card: BaseCard) -> None:
        """Ложит карту на вершину стопки."""
        if self.top is None:
            self.top = card

        self.used_cards.append(self.top)
        self.top = card

    # Наполнение колоды
    # =================

    def fill_classic(self) -> None:
        """Наполняет колоду классическим набором карт."""
        logger.info("Add classic card set in deck")
        self.clear()

        # Нули добавляем отдельно поскольку их всегда по одному
        for c in (0, 1, 2, 3):
            self.cards.append(NumberCard(CardColor(c), 0))

        # Добавляем по два набора всех остальных карт
        for _ in range(2):
            for c in (0, 1, 2, 3):
                for value in range(10):
                    self.cards.append(NumberCard(CardColor(c), value))
                self.cards.append(ReverseCard(CardColor(c)))
                self.cards.append(TurnCard(CardColor(c), 1))
                self.cards.append(TakeCard(CardColor(c)))

        # Добавляем козырные карты
        for _ in (0, 1, 2, 3):
            self.cards.append(ChooseColorCard())
            self.cards.append(TakeFourCard())

        self.shuffle()

    def fill_wild(self) -> None:
        """Наполняет колоду диким набором карт."""
        logger.info("Add wild card set in deck")
        self.clear()
        # Добавляем по 4 набора диких карт
        for _ in (0, 1, 2, 3):
            for c in (0, 1, 2, 3):
                for value in range(6):
                    self.cards.append(NumberCard(CardColor(c), value))
                self.cards.append(ReverseCard(CardColor(c)))
                self.cards.append(TurnCard(CardColor(c), 1))
                self.cards.append(TakeCard(CardColor(c)))

        # Добавляем козырные карты
        for _ in range(6):
            self.cards.append(ChooseColorCard())
            self.cards.append(TakeFourCard())
        self.shuffle()
