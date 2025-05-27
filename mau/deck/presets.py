"""Генератор колоды.

Более высокоуровневый класс, для генерации колоды по выбранным правилам
или по готовым шаблонам.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Self

from mau.deck import behavior
from mau.deck.card import MauCard
from mau.deck.deck import Deck
from mau.enums import CardColor


@dataclass(slots=True, frozen=True)
class CardGroup:
    """Группа карт.

    Обобщённо описывает карты. которые должны быть.
    Тип карты, значение, цвета, и их количество в колоде.

    К примеру: Числовые карты всех цветов по две на каждый цвет.
    """

    behavior: behavior.NumberBehavior
    value: int
    colors: Iterable[CardColor]
    count: int

    def cards(self) -> Iterator[MauCard]:
        """Преобразует группу карт в итератор экземпляров карт.

        Если было указано по 3 карты всех цветов, то он вернёт 12 карт.
        """
        for count in range(self.count):
            for color in self.colors:
                yield MauCard(
                    color,
                    self.value,
                    self.behavior.cost or self.value,
                    self.behavior,
                )


@dataclass(slots=True, frozen=True)
class DeckPreset:
    """Шаблон колоды.

    Содержит готовые правила формирования колоды, которые можно
    использовать в игре.
    """

    name: str
    desc: str
    groups: Iterable[CardGroup]


# Пресеты колод
# =============

ALL_COLORS = (CardColor.RED, CardColor.YELLOW, CardColor.GREEN, CardColor.CYAN)

_NUMBER = behavior.NumberBehavior()
_TWIST = behavior.TwistBehavior()
_ROTATE = behavior.RotateBehavior()
_REVERSE = behavior.ReverseBehavior()
_TURN = behavior.TurnBehavior()
_TAKE = behavior.TakeBehavior()
_TAKE_FOUR = behavior.WildTakeBehavior()
_COLOR = behavior.WildColorBehavior()

# Все готовые пресеты колод
# TODO: Хранить в каких-нибудь настройках
CARD_PRESETS: dict[str, DeckPreset] = {
    "classic": DeckPreset(
        name="🎻 Классика",
        desc="Стандартная колода Уно",
        groups=(
            CardGroup(_ROTATE, 0, ALL_COLORS, 1),
            CardGroup(_NUMBER, 1, ALL_COLORS, 2),
            CardGroup(_TWIST, 2, ALL_COLORS, 2),
            CardGroup(_NUMBER, 3, ALL_COLORS, 2),
            CardGroup(_NUMBER, 4, ALL_COLORS, 2),
            CardGroup(_NUMBER, 5, ALL_COLORS, 2),
            CardGroup(_NUMBER, 6, ALL_COLORS, 2),
            CardGroup(_NUMBER, 7, ALL_COLORS, 2),
            CardGroup(_NUMBER, 8, ALL_COLORS, 2),
            CardGroup(_NUMBER, 9, ALL_COLORS, 2),
            CardGroup(_REVERSE, 1, ALL_COLORS, 2),
            CardGroup(_TURN, 1, ALL_COLORS, 2),
            CardGroup(_TAKE, 2, ALL_COLORS, 2),
            CardGroup(_TAKE_FOUR, 4, [CardColor.BLACK], 4),
            CardGroup(_COLOR, 0, [CardColor.BLACK], 4),
        ),
    ),
    "wild": DeckPreset(
        name="🐍 Дикие карты",
        desc="Меньше цифр, больше действий.",
        groups=(
            CardGroup(_ROTATE, 0, ALL_COLORS, 4),
            CardGroup(_NUMBER, 1, ALL_COLORS, 4),
            CardGroup(_TWIST, 2, ALL_COLORS, 4),
            CardGroup(_NUMBER, 3, ALL_COLORS, 4),
            CardGroup(_NUMBER, 4, ALL_COLORS, 4),
            CardGroup(_NUMBER, 5, ALL_COLORS, 4),
            CardGroup(_REVERSE, 1, ALL_COLORS, 4),
            CardGroup(_TURN, 1, ALL_COLORS, 4),
            CardGroup(_TAKE, 2, ALL_COLORS, 4),
            CardGroup(_TAKE_FOUR, 4, [CardColor.BLACK], 6),
            CardGroup(_COLOR, 0, [CardColor.BLACK], 6),
        ),
    ),
    "casino": DeckPreset(
        name="🎰 Казино",
        desc="Нет слов, одни эмоции.",
        groups=(
            CardGroup(_ROTATE, 0, ALL_COLORS, 4),
            CardGroup(_NUMBER, 1, ALL_COLORS, 4),
            CardGroup(_TWIST, 2, ALL_COLORS, 4),
            CardGroup(_NUMBER, 3, ALL_COLORS, 4),
            CardGroup(_NUMBER, 4, ALL_COLORS, 4),
            CardGroup(_NUMBER, 5, ALL_COLORS, 4),
            CardGroup(_REVERSE, 1, ALL_COLORS, 6),
            CardGroup(_TURN, 1, ALL_COLORS, 6),
            CardGroup(_TAKE, 2, ALL_COLORS, 6),
            CardGroup(_TAKE_FOUR, 4, [CardColor.BLACK], 8),
            CardGroup(_COLOR, 0, [CardColor.BLACK], 8),
        ),
    ),
    "single": DeckPreset(
        name="🗑️ Отладочные",
        desc="По одной карте для каждого типа.",
        groups=(
            CardGroup(_ROTATE, 0, ALL_COLORS, 1),
            CardGroup(_NUMBER, 1, ALL_COLORS, 1),
            CardGroup(_TWIST, 2, ALL_COLORS, 1),
            CardGroup(_NUMBER, 3, ALL_COLORS, 1),
            CardGroup(_NUMBER, 4, ALL_COLORS, 1),
            CardGroup(_NUMBER, 5, ALL_COLORS, 1),
            CardGroup(_NUMBER, 6, ALL_COLORS, 1),
            CardGroup(_NUMBER, 7, ALL_COLORS, 1),
            CardGroup(_NUMBER, 8, ALL_COLORS, 1),
            CardGroup(_NUMBER, 9, ALL_COLORS, 1),
            CardGroup(_REVERSE, 1, ALL_COLORS, 1),
            CardGroup(_TURN, 1, ALL_COLORS, 1),
            CardGroup(_TAKE, 2, ALL_COLORS, 1),
            CardGroup(_TAKE_FOUR, 4, [CardColor.BLACK], 1),
            CardGroup(_COLOR, 0, [CardColor.BLACK], 1),
        ),
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

    def _cards(self) -> Iterator[MauCard]:
        """Получает полный список карт для всего шаблона со всех групп."""
        for group in self.groups:
            yield from group.cards()

    @property
    def deck(self) -> Deck:
        """Собирает новую колоду из правил."""
        return Deck(list(self._cards()))

    @classmethod
    def from_preset(cls, preset_name: str) -> Self:
        """Получает новый генератор колоды по названию шаблона."""
        return cls(list(CARD_PRESETS[preset_name].groups), preset_name)
