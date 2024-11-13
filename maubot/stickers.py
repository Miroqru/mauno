"""Стикерпак UNO.

Хранит в себе таблицу всех стикеров из стикерпака.
А также предоставляет методы для сериализации/десериализации карт Уно.
"""

import re
from typing import NamedTuple

from maubot.uno.card import (
    BaseCard,
    CardColor,
    ChooseColorCard,
    NumberCard,
    ReverseCard,
    TakeCard,
    TakeFourCard,
    TurnCard,
)

# Таблица стикеров
# ================

NORMAL = {
    "color": "CAADAgADLV0AAoa8aEnWTgiOOj_X-AI",
    "take_four": "CAADAgADL2QAAkppaEkmy1ZFZDL6agI",

    "take0": "CAADAgADiFoAAkiMaEns7jTQDVI5DgI",
    "take1": "CAADAgADtmYAAksKaUkej4If1HjqsQI",
    "take2": "CAADAgADxmMAAhj2aUkapOvXS7aFRQI",
    "take3": "CAADAgADQWAAAl3paUkx0IL1fHvLnwI",

    "reverse0": "CAADAgADAWMAAikOYEmDR_QQ7AABdHkC",
    "reverse1": "CAADAgADx1wAAuFaaEkyJjcJ2V2i-wI",
    "reverse2": "CAADAgADO1gAAjCKaElVdF90GpJkLAI",
    "reverse3": "CAADAgADDFwAAt26aEkodi50VNrdEAI",

    "skip0": "CAADAgADk10AAhY8aElof7bmbvcnPAI",
    "skip1": "CAADAgADIGMAAmd3aEnD6omtxRkSIwI",
    "skip2": "CAADAgAD1FsAAkIaaUncotvBqx1aXAI",
    "skip3": "CAADAgADx24AAqo1aEm-993LRWNXUwI",

    # Red number cards
    "00": "CAADAgADBmMAArRBaElwMzXDyh5TRQI",
    "01": "CAADAgAD3mMAApwxaUmeEycLntbJ9AI",
    "02": "CAADAgADfVgAAoSUaEnPtdohyJdp-QI",
    "03": "CAADAgADm2EAAmdjaUlL_dbd1w1MsAI",
    "04": "CAADAgADM2IAAn7CaUmYxLJTmXb4zgI",
    "05": "CAADAgADaVwAAiZ0aEmfhVMrmSa1ugI",
    "06": "CAADAgADqGsAAqpxaUnM9xRYVjgHUgI",
    "07": "CAADAgADiVkAAlpzaUkdrBhsrb8uxgI",
    "08": "CAADAgAD8F8AAikBaUnf9qXSHCvPvgI",
    "09": "CAADAgADumgAAhvMaEkjiV1DXeqEuwI",

    # Yellow number cards
    "10": "CAADAgAD3GAAAi3baElq2AZUE-T-AgI",
    "11": "CAADAgADZGUAAj7HaEkAAVV0FEu49qgC",
    "12": "CAADAgADx2IAAu-OaUnhkUO_-Y6DIgI",
    "13": "CAADAgADGV4AAue5aEmMgL0o2SN3DQI",
    "14": "CAADAgAD8l0AAhBNaUnA9vfUFKBeQQI",
    "15": "CAADAgADIWMAAvN8aUmTvGioQAoXPgI",
    "16": "CAADAgAD4GcAAnLpaUnJfMtYnNbcDAI",
    "17": "CAADAgAEXAACdeJoSX-JOi-1ZWnMAg",
    "18": "CAADAgAD1WkAAnooaUmlvNaBzYhAgQI",
    "19": "CAADAgADCVMAAgNbaEnfZBZ5dy8B8QI",

    # Green number cards
    "20": "CAADAgADKWMAAssRaEkStDq0EUlljgI",
    "21": "CAADAgAD63YAAtz3aUlJ7q0VYF5MzAI",
    "22": "CAADAgADpnAAAvDEaEnAHngF_LaW2wI",
    "23": "CAADAgADX2UAAiD1aUlw-cO0LtErwQI",
    "24": "CAADAgADmlkAAi4QaUla8U8nwQl7MgI",
    "25": "CAADAgADbFwAAtXaaUkH2I86VzQKwQI",
    "26": "CAADAgADHFkAAm_7aUm0I7-pxWbzMAI",
    "27": "CAADAgADa2IAAsJCaUlCMbsCEMHgvQI",
    "28": "CAADAgADKF8AAid4aElAuvnFv4RZngI",
    "29": "CAADAgADy1gAAvYmaEnAaDCWq37o5gI",

    # Blue number cards
    "30": "CAADAgADZ1gAAoRqaUnRixlEAywPnwI",
    "31": "CAADAgADnWMAAn5kaElP2J_f3OK-DwI",
    "32": "CAADAgADi1wAAg5NaEnQ2uNUSYVpewI",
    "33": "CAADAgADp2AAAmXcaUlB3bqTCHhmQwI",
    "34": "CAADAgAD9GIAAjJJaEmPvdLKTQAB8usC",
    "35": "CAADAgADBmYAApx4aUm0asm6l8KO-AI",
    "36": "CAADAgADk2MAAuPlaElUotP5J8-lDQI",
    "37": "CAADAgADtGQAAjzGaUlTWW33svpz7AI",
    "38": "CAADAgADgFwAAl-RaUlBXu5Y8XpRjgI",
    "39": "CAADAgADIGIAAlH0aUlnbTrlxr4bogI",
}

NOT_PLAYABLE = {
    "color": "CAADAgAD22IAAlBmaUmR6oS5M0fwDwI",
    "take_four": "CAADAgADe2MAAuVKaEniBMzksrl8CAI",
}


# Стикеры для обозначения опций
# =============================

class OptionStickers(NamedTuple):
    """Стикеры для специальных действий во время игры.

    bluff - обвинить другого игрока во лжи, когда он разыграл +4
    draw - Взять карту из колоды.
    info - Посмотреть текущий статус игры.
    pass - Передать ход следующему игроку / пропустить.
    """

    bluff: str
    draw: str
    info: str
    next_turn: str

OPTIONS = OptionStickers(
    bluff = "CAADAgADkmcAAttjaEmfg1PaY1hvyAI",
    draw = "CAADAgADwmkAArcyaUnnzpUUU7YQYAI",
    info = "CAADAgADkmAAAv-aaUlM0SwReOh3WwI",
    next_turn = "CAADAgADJl8AAsMIaEl7l8IZc-EdXwI",
)


# Вспомогательные функции
# =======================

# Паттерны для сопоставления
# Обычные числовые карты обрабатываются последними
skip_pattern = re.compile(r"skip([0-5])(\d)")
take_pattern = re.compile(r"take([0-5])(\d)")
reverse_pattern = re.compile(r"reverse([0-5])")
number_pattern = re.compile(r"([0-5])(\d)")

def to_str(card: BaseCard) -> str:
    """Превращает карту в строковый ID.

    После он будет использоваться чтобы отправить нужный стикер.
    """
    if isinstance(card, NumberCard):
        return f"{card.color.value}{card.value}" # 00 .. # 59
    elif isinstance(card, TurnCard):
        return f"skip{card.color.value}"
    elif isinstance(card, ReverseCard):
        return f"reverse{card.color.value}"
    elif isinstance(card, TakeCard):
        return f"take{card.color.value}"
    elif isinstance(card, ChooseColorCard):
        return "color"
    elif isinstance(card, TakeFourCard):
        return "take_four"

# TODO: Метод обратного преобразования из строки
# def from_str(card_str: str) -> BaseCard:
#     """Превращает строку карты в действительный экземпляр."""
#     groups = skip_pattern.match(card_str).groups()
#     if groups is not None:
#         return TurnCard(CardColor(int(groups[0])), int(groups[1]))

#     groups = take_pattern.match(card_str).groups()
#     if groups is not None:
#         return TakeCard(CardColor(int(groups[0])), int(groups[1]))

#     groups = reverse_pattern.match(card_str).groups()
#     if groups is not None:
#         return ReverseCard(CardColor(int(groups[0])))

#     groups = number_pattern.match(card_str).groups()
#     if groups is not None:
#         return NumberCard(CardColor(int(groups[0])), int(groups[1]))
