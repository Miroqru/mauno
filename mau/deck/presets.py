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

    Несколько карт одного поведения, стоимости и значения.
    Но с разными параметрами цвета и количества.
    """

    value: int
    """Значение карты.

    Влияет на её поведение.
    Для числовых карт обозначает номер.
    Для карт взятия - сколько нужно взять карт.
    И по подобной логике.
    """

    cost: int
    """Общая стоимость для карты.

    Стоимость описывает насколько карта ценная.
    Это используется при сортировке. подсчёте очков и специальном режиме.
    """

    colors: Iterable[CardColor]
    """Каких цветов надо добавлять карты в группе."""

    count: int
    """Сколько одинаковых карт будет в группе.

    К примеру числовых карт может быть по два экземпляр.
    А диких по 4.
    """

    behavior: CardBehavior
    """Поведение карты.

    Какой из выбранных поведений будет применяться к карте.
    """

    def cards(self) -> Iterator[MauCard]:
        """Преобразует группу карт в итератор экземпляров карт.

        Если было указано по 3 карты всех цветов, то он вернёт 12 карт.
        """
        for _ in range(self.count):
            for color in self.colors:
                yield MauCard(color, self.value, self.cost, self.behavior)


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
