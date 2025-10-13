"""Игровые карты Mau."""

from dataclasses import dataclass
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


@dataclass(slots=True)
class MauCard:
    """Описание каждой карты Mau.

    Предоставляет общий функционал для всех карт.
    """

    color: CardColor
    value: int
    cost: int
    behavior: CardBehavior

    def can_cover(self, other_card: Self, wild_color: CardColor) -> bool:
        """Проверяет что другая карта может покрыть текущую.

        По правилам игры цель каждого игрока - избавить от своих карт.
        Чтобы избавиться от карт, нужно накрыть текущую карту с
        верхушки одной из своей руки.
        Как только карты кончатся - вы победили.
        """
        return other_card.color in (wild_color, self.color) or (
            self.behavior.name == other_card.behavior.name
            and self.value == other_card.value
        )

    def on_use(self, game: "MauGame") -> None:
        """Выполняет активное действие карты во время её разыгрывания."""
        for call in self.behavior.use:
            call(game, self)

    def on_cover(self, game: "MauGame") -> None:
        """Подготавливает карту к повторному использованию в колоде."""
        for call in self.behavior.cover:
            call(game, self)

    __call__ = on_use
