"""Игровые карты Mau."""

import re
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Self

from mau.deck import behavior
from mau.deck.behavior import BaseWildBehavior, NumberBehavior
from mau.enums import CardColor

if TYPE_CHECKING:
    from mau.deck.deck import Deck
    from mau.game.game import MauGame

# TODO: Какой-то костыль
CARD_REGEX = re.compile(r"(\d)_(\d+)_(\d+)_([a-z+]+)")
CARD_BEHAVIOR = {
    "rotate": behavior.RotateBehavior,
    "twist": behavior.TwistBehavior,
    "number": behavior.NumberBehavior,
    "turn": behavior.TurnBehavior,
    "reverse": behavior.ReverseBehavior,
    "take": behavior.TakeBehavior,
    "wild+color": behavior.WildColorBehavior,
    "wild+take": behavior.WildTakeBehavior,
}


class MauCard:
    """Описание каждой карты Mau.

    Предоставляет общий функционал для всех карт.
    """

    __slots__ = ("color", "value", "cost", "behavior")

    def __init__(
        self, color: CardColor, value: int, cost: int, behavior: NumberBehavior
    ) -> None:
        self.color = color
        self.value = value
        self.cost = cost
        self.behavior = behavior

    @classmethod
    def unpack(cls, card_str: str) -> Self | None:
        """Превращает упакованную строку карты в её экземпляр.

        Обратное действие для получения экземпляра карты из строки.
        Используется уже при обработке отправленного стикеров.
        """
        card_match = CARD_REGEX.match(card_str)
        if card_match is None:
            return None

        # TODO: Изменить формат карты
        color, value, cost, card_behavior = card_match.groups()
        card_behavior = CARD_BEHAVIOR[card_behavior]

        return cls(
            color=CardColor(int(color)),
            value=int(value),
            cost=card_behavior.cost or int(value),
            behavior=card_behavior(),
        )

    def pack(self) -> str:
        """запаковывает карту в строку."""
        return (
            f"{self.color.value}_{self.value}_{self.cost}_{self.behavior.name}"
        )

    def can_cover(self, other_card: Self, wild_color: CardColor) -> bool:
        """Проверяет что другая карта может покрыть текущую.

        По правилам игры цель каждого игрока - избавить от своих карт.
        Чтобы избавиться от карт, нужно накрыть текущую карту с
        верхушки одной из своей руки.
        Как только карты кончатся - вы победили.
        """
        return (
            isinstance(other_card.behavior, BaseWildBehavior)
            or other_card.color in (wild_color, self.color)
            or (
                self.behavior == other_card.behavior
                and self.value == other_card.value
            )
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

    def use(self, game: "MauGame") -> None:
        """Выполняет активное действие карты во время её разыгрывания."""
        self.behavior.use(self, game)

    def prepare_used(self, deck: "Deck") -> None:
        """Подготавливает карту к повторному использованию в колоде."""
        self.behavior.prepare_used(self, deck)

    def __repr__(self) -> str:
        """Представление карты для отладки."""
        return (
            f"MauCard<{self.color}, {self.value}, {self.cost}, {self.behavior}>"
        )

    __call__ = use

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
