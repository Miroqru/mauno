"""Стикерпак UNO.

Хранит в себе таблицу всех стикеров из стикерпака.
А также предоставляет методы для сериализации/десериализации карт Уно.
"""

import re

from maubot.uno.card import CardColor, BaseCard, TakeCard, TurnCard, TakeFourCard, ChooseColorCard, NumberCard


# Стикеры для специальных действий
# bluff - обвинить другого игрока во лжи, когда он разыграл +4
# draw - Взять карту из колоды.
# info - Посмотреть текущий статус игры.
# pass - Передать ход следующему игроку / пропустить.
OPTIONS = {
    "bluff": "CAADAgADkmcAAttjaEmfg1PaY1hvyAI",
    "draw": "CAADAgADwmkAArcyaUnnzpUUU7YQYAI",
    "info": "CAADAgADkmAAAv-aaUlM0SwReOh3WwI",
    "pass": "CAADAgADJl8AAsMIaEl7l8IZc-EdXwI",
}

# Вспомогательные функции
# =======================

def to_str(card: BaseCard) -> str:
    """Превращает карту в строковое представление."""
    if isinstance(card, NumberCard):
        return f"{card.color.value}_{card.value}" # 0_0 .. # 5_9