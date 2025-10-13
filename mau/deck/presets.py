"""Генератор колоды.

Более высокоуровневый класс, для генерации колоды по выбранным правилам
или по готовым шаблонам.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from mau.deck.behavior import CardBehavior
from mau.deck.card import CardColor, MauCard
from mau.deck.deck import Deck


@dataclass(slots=True, frozen=True)
class CardGroup:
    """Группа карт.

    Обобщённо описывает несколько карт. которые должны быть в колоде.
    Тип карты, значение, цвета, и их количество в колоде.
    """

    behavior: CardBehavior
    value: int
    colors: Iterable[CardColor]
    count: int

    def cards(self) -> Iterator[MauCard]:
        """Преобразует группу карт в итератор экземпляров карт.

        Если было указано по 3 карты всех цветов, то он вернёт 12 карт.
        """
        for _ in range(self.count):
            for color in self.colors:
                yield MauCard(color, self.value, self.value, self.behavior)


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
