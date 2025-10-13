"""Игровые карты Mau."""

from collections.abc import Iterable, Iterator
from enum import IntEnum
from typing import TYPE_CHECKING, Self

from mau.deck.behavior import CardBehavior

if TYPE_CHECKING:
    from mau.game.game import MauGame


class CardColor(IntEnum):
    """Цвета карты.

    У каждой карты обязательно есть цвет для отличия от других карт.
    В классическом режиме используются красный, жёлтый, зелёный, синий,
    а чёрный цвет используется как козырный.
    Это значит что он кроет любую карту.

    Настройки цветов карт можно переопределить настройками игры.
    то значит что козырным цветом может быть любая карта.
    """

    RED = 0
    ORANGE = 1
    YELLOW = 2
    GREEN = 3
    CYAN = 4
    BLUE = 5
    BLACK = 6
    CREAM = 7


class MauCard:
    """Описание каждой карты Mau.

    Предоставляет общий функционал для всех карт.
    """

    __slots__ = ("color", "value", "cost", "behavior")

    def __init__(
        self, color: CardColor, value: int, cost: int, behavior: CardBehavior
    ) -> None:
        self.color = color
        self.value = value
        self.cost = cost
        self.behavior = behavior

    def can_cover(self, other_card: Self, wild_color: CardColor) -> bool:
        """Проверяет что другая карта может покрыть текущую.

        По правилам игры цель каждого игрока - избавить от своих карт.
        Чтобы избавиться от карт, нужно накрыть текущую карту с
        верхушки одной из своей руки.
        Как только карты кончатся - вы победили.
        """
        return other_card.color in (wild_color, self.color) or (
            self.behavior == other_card.behavior
            and self.value == other_card.value
        )

    # TODO: Тебя бы использовать по хорошему
    def iter_covering(
        self, hand: Iterable[Self], wild_color: CardColor
    ) -> Iterator[tuple[Self, bool]]:
        """Проверяет какие карты вы можете покрыть из своей руки.

        Используется чтобы проверить всю свою руку на наличие карт,
        которыми можно покрыть текущую.

        Args:
            hand (Iterable[BaseCard]): Карты в вашей руке.
            wild_color (CardColor): какой сейчас дикий цвет.

        Yields:
            Iterator[BaseCard, bool]: Возвращает карту и можете ли вы
                ею покрыть текущую.

        """
        yield from ((card, self.can_cover(card, wild_color)) for card in hand)

    def on_use(self, game: "MauGame") -> None:
        """Выполняет активное действие карты во время её разыгрывания."""
        for call in self.behavior.use:
            call(game, self)

    def on_cover(self, game: "MauGame") -> None:
        """Подготавливает карту к повторному использованию в колоде."""
        for call in self.behavior.cover:
            call(game, self)

    def __repr__(self) -> str:
        """Представление карты для отладки."""
        return (
            f"MauCard<{self.color}, {self.value}, {self.cost}, {self.behavior}>"
        )

    __call__ = on_use

    def __eq__(self, other: object) -> bool:
        """Проверяет соответствие двух карт."""
        if not isinstance(other, MauCard):
            return NotImplemented

        return (
            self.color == other.color
            and self.behavior == other.behavior
            and self.value == other.value
        )

    def __lt__(self, other_card: object) -> bool:
        """Проверяет что данная карта меньшей стоимости чем прочая."""
        if not isinstance(other_card, MauCard):
            return NotImplemented

        return (
            self.color < other_card.color
            and self.value < other_card.value
            and self.cost < other_card.cost
        )
