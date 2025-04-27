"""Генератор карт для колоды."""

import re

from mau.deck import behavior
from mau.deck.card import UnoCard
from mau.enums import CardColor, CardType

CARD_REGEX = re.compile(r"(\d)([0-4])(\d)")
TWIST_NUMBER = 2
ROTATE_NUMBER = 0

DEFAULT_BEHAVIOR = (
    behavior.UnoBehavior,
    behavior.TurnBehavior,
    behavior.ReverseBehavior,
    behavior.TakeBehavior,
    behavior.ColorBehavior,
    behavior.ColorTakeBehavior,
)


def default_behavior(card_type: CardType, value: int) -> behavior.UnoBehavior:
    """Получает стандартное поведение для карты."""
    if card_type == CardType.NUMBER and value == TWIST_NUMBER:
        return behavior.TwistBehavior()
    elif card_type == CardType.NUMBER and value == ROTATE_NUMBER:
        return behavior.TwistBehavior()
    return DEFAULT_BEHAVIOR[card_type.value]()


def get_card(card_type: CardType, color: CardColor, value: int) -> UnoCard:
    """Вернёт карту со стандартным поведением."""
    return UnoCard(
        card_type=card_type,
        color=color,
        value=value,
        cost=card_type.cost or value,
        behavior=default_behavior(card_type, value),
    )


def card_from_str(card_str: str) -> UnoCard | None:
    """Превращает упакованную строку карты в её экземпляр.

    Обратное действие для получения экземпляра карты из строки.
    Используется уже при обработке отправленного стикеров.
    """
    card_match = CARD_REGEX.match(card_str)
    if card_match is None:
        return None

    c_type, color, value = (int(group) for group in card_match.groups())
    return get_card(CardType(c_type), CardColor(color), value)
