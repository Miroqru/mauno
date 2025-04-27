"""Карта Uno."""

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Self

from mau.deck.behavior import UnoBehavior
from mau.enums import CardColor, CardType

if TYPE_CHECKING:
    from mau.game.game import UnoGame


class UnoCard:
    """Описание каждой карты Uno.

    Предоставляет общий функционал для всех карт.
    """

    __slots__ = ("color", "card_type", "value", "cost", "behavior")

    def __init__(
        self,
        color: CardColor,
        card_type: CardType,
        value: int,
        cost: int,
        behavior: UnoBehavior,
    ) -> None:
        self.color: CardColor = color
        self.card_type: CardType = card_type
        self.value: int = value
        self.cost: int = cost
        self.behavior = behavior

    def can_cover(self, other_card: Self) -> bool:
        """Проверяет что другая карта может покрыть текущую.

        По правилам игры цель каждого игрока - избавить от своих карт.
        Чтобы избавиться от карт, нужно накрыть текущую карту с
        верхушки одной из своей руки.
        Как только карты кончатся - вы победили.
        """
        return (
            other_card.card_type in (CardType.CHOOSE_COLOR, CardType.TAKE_FOUR)
            or self.color == other_card.color
            or (
                self.card_type == other_card.card_type
                and self.value == other_card.value
            )
        )

    def iter_covering(
        self, hand: Iterable[Self]
    ) -> Iterator[tuple[Self, bool]]:
        """Проверяет какие карты вы можете покрыть из своей руки.

        Используется чтобы проверить всю свою руку на наличие карт,
        которыми можно покрыть текущую.

        Args:
            hand (Iterable[BaseCard]): Карты в вашей руке.

        Yields:
            Iterator[BaseCard, bool]: Возвращает карту и можете ли вы
                ею покрыть текущую.

        """
        yield from ((card, self.can_cover(card)) for card in hand)

    def use(self, game: "UnoGame") -> None:
        """Выполняет активное действие карты во время её разыгрывания."""
        self.behavior.use(self, game)

    def prepare_used(self) -> None:
        """Подготавливает карту к повторному использованию в колоде."""
        self.behavior.prepare_used(self)

    def to_str(self) -> str:
        """запаковывает карту в строку."""
        return f"{self.card_type.value}{self.color.value}{self.value}"

    def __call__(self, game: "UnoGame") -> None:
        """Синтаксический сахар для вызова действия карты.

        Позволяет использовать способность этой карты.
        Является сокращением для метода use_card.
        """
        return self.use(game)

    def __str__(self) -> str:
        """Представление карты в строковом виде."""
        return f"{self.color} {self.card_type} {self.value}"

    def __repr__(self) -> str:
        """Представление карты при отладке."""
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """Проверяет соответствие двух карт."""
        if not isinstance(other, UnoCard):
            return NotImplemented

        return (
            (
                self.color == other.color
                or other.card_type
                in (CardType.CHOOSE_COLOR, CardType.TAKE_FOUR)
            )
            and self.card_type == other.card_type
            and self.value == other.value
        )

    def __lt__(self, other_card: object) -> bool:
        """Проверяет что данная карта меньшей стоимости чем прочая."""
        if not isinstance(other_card, UnoCard):
            return NotImplemented

        return (
            self.color < other_card.color
            and self.value < other_card.value
            and self.cost < other_card.cost
        )
