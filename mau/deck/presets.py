"""Генератор колоды.

Более высокоуровневый класс, для генерации колоды по выбранным правилам
или по готовым шаблонам.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Self

from mau.card import (
    BaseCard,
    CardColor,
    CardType,
    ChooseColorCard,
    NumberCard,
    ReverseCard,
    TakeCard,
    TakeFourCard,
    TurnCard,
)
from mau.deck import Deck


@dataclass(slots=True, frozen=True)
class CardGroup:
    """Группа карт.

    Обобщённо описывает карты. которые должны быть.
    Тип карты, значение, цвета, и их количество в колоде.

    К примеру: Числовые карты всех цветов по две на каждый цвет.
    """

    card_type: CardType
    value: int
    colors: list[CardColor]
    count: int

    def _to_card(self, color: CardColor, value: int) -> BaseCard:
        if self.card_type == CardType.NUMBER:
            return NumberCard(color, value)
        elif self.card_type == CardType.TURN:
            return TurnCard(color, value)
        elif self.card_type == CardType.REVERSE:
            return ReverseCard(color)
        elif self.card_type == CardType.TAKE:
            return TakeCard(color, value)
        elif self.card_type == CardType.CHOOSE_COLOR:
            return ChooseColorCard()
        elif self.card_type == CardType.TAKE_FOUR:
            return TakeFourCard()
        raise ValueError("Unknown card type")

    def get_cards(self) -> Iterator[BaseCard]:
        """Преобразует группу карт в итератор экземпляров карт.

        Если было указано по 3 карты всех цветов, то он вернёт 12 карт.
        """
        for count in range(self.count):
            for color in self.colors:
                yield self._to_card(color, self.value)


@dataclass(slots=True, frozen=True)
class DeckPreset:
    """Шаблон колоды.

    Содержит готовые правила формирования колоды, которые можно
    использовать в игре.
    """

    name: str
    desc: str
    groups: list[CardGroup]


# Пресеты колод
# =============

ALL_COLORS = [CardColor.RED, CardColor.YELLOW, CardColor.GREEN, CardColor.BLUE]

# Все готовые пресеты колод
CARD_PRESETS: dict[str, DeckPreset] = {
    "classic": DeckPreset(
        name="🎻 Классика",
        desc="Стандартная колода Уно",
        groups=[
            CardGroup(CardType.NUMBER, 0, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 1, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 2, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 3, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 4, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 5, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 6, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 7, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 8, ALL_COLORS, 2),
            CardGroup(CardType.NUMBER, 9, ALL_COLORS, 2),
            CardGroup(CardType.REVERSE, 1, ALL_COLORS, 2),
            CardGroup(CardType.TURN, 1, ALL_COLORS, 2),
            CardGroup(CardType.TAKE, 2, ALL_COLORS, 2),
            CardGroup(CardType.TAKE_FOUR, 0, [CardColor.BLACK], 4),
            CardGroup(CardType.CHOOSE_COLOR, 0, [CardColor.BLACK], 4),
        ],
    ),
    "wild": DeckPreset(
        name="🐍 Дикие карты",
        desc="Меньше цифр, больше действий.",
        groups=[
            CardGroup(CardType.NUMBER, 0, ALL_COLORS, 4),
            CardGroup(CardType.NUMBER, 1, ALL_COLORS, 4),
            CardGroup(CardType.NUMBER, 2, ALL_COLORS, 4),
            CardGroup(CardType.NUMBER, 3, ALL_COLORS, 4),
            CardGroup(CardType.NUMBER, 4, ALL_COLORS, 4),
            CardGroup(CardType.NUMBER, 5, ALL_COLORS, 4),
            CardGroup(CardType.REVERSE, 1, ALL_COLORS, 4),
            CardGroup(CardType.TURN, 1, ALL_COLORS, 4),
            CardGroup(CardType.TAKE, 2, ALL_COLORS, 4),
            CardGroup(CardType.TAKE_FOUR, 0, [CardColor.BLACK], 6),
            CardGroup(CardType.CHOOSE_COLOR, 0, [CardColor.BLACK], 6),
        ],
    ),
    "single": DeckPreset(
        name="🗑️ Отладочные",
        desc="По одной карте для каждого типа.",
        groups=[
            CardGroup(CardType.NUMBER, 0, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 1, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 2, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 3, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 4, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 5, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 6, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 7, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 8, ALL_COLORS, 1),
            CardGroup(CardType.NUMBER, 9, ALL_COLORS, 1),
            CardGroup(CardType.REVERSE, 1, ALL_COLORS, 1),
            CardGroup(CardType.TURN, 1, ALL_COLORS, 1),
            CardGroup(CardType.TAKE, 2, ALL_COLORS, 1),
            CardGroup(CardType.TAKE_FOUR, 0, [CardColor.BLACK], 1),
            CardGroup(CardType.CHOOSE_COLOR, 0, [CardColor.BLACK], 1),
        ],
    ),
}


class DeckGenerator:
    """Генератор колоды.

    Собирает колоду карт, используя группы карт.
    Позволяет редактировать правила сборки колоды.
    """

    def __init__(
        self,
        groups: list[CardGroup] | None = None,
        preset_name: str = "custom",
    ) -> None:
        self.groups: list[CardGroup] = groups or []
        self.preset_name = preset_name

    def _get_cards(self) -> list[BaseCard]:
        res = []

        for group in self.groups:
            for card in group.get_cards():
                res.append(card)
        return res

    def get_deck(self) -> Deck:
        """Собирает новую колоду из правил."""
        return Deck(self._get_cards())

    @classmethod
    def from_preset(cls, preset_name: str) -> Self:
        """Получает новый генератор колоды по названию шаблона."""
        return cls(CARD_PRESETS[preset_name].groups, preset_name)
