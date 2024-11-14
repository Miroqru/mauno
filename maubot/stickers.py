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

    "take0": "CAADAgAD9mQAAtnnYUlEpboCdX8qrAI",
    "take1": "CAADAgADJGAAAnMXaEkIuKQWnVoHVAI",
    "take2": "CAADAgADFGIAAtADaEn_WWFq49idHQI",
    "take3": "CAADAgADX1wAAslNaEkF16twdqHJCQI",

    "reverse0": "CAADAgADWloAAjjNaUlWXvrnmEy3xwI",
    "reverse1": "CAADAgAD514AAg0LaEmCIOaD-A2JiQI",
    "reverse2": "CAADAgADkVsAAl4baEnQmC8B7PLk7gI",
    "reverse3": "CAADAgADmmAAApQ4aEm-DEug76oHAQI",

    "skip0": "CAADAgADCWgAAvsHaUl7v6RBUl8PlAI",
    "skip1": "CAADAgADN1wAAi50aUnbZeAAAUpdIN0C",
    "skip2": "CAADAgADu14AAn3fYUmgC__ZYoW3wwI",
    "skip3": "CAADAgADdV4AAjL0aEl--q81vXlCMwI",

    # Red number cards
    "00": "CAADAgAD9l8AAqG-aEm1N0MDmDKmuQI",
    "01": "CAADAgADCl8AAkmuaUluF1n2I8-47wI",
    "02": "CAADAgADrmAAAqmLaUn_xH_m5MZCGAI",
    "03": "CAADAgADLGUAAl8MaEln0qeSdyHJvAI",
    "04": "CAADAgADJFwAArrlaUnNgARazALoSwI",
    "05": "CAADAgADXmUAAqT9aUniTrgZNO6VQwI",
    "06": "CAADAgAD_18AAsbNaUmQtV8W1Rnl1AI",
    "07": "CAADAgAD8GQAAlsEaUmuWtwLO1Lk6QI",
    "08": "CAADAgAD714AAvn6aUmMH4kb0r2N5gI",
    "09": "CAADAgADQGAAAgKPaEmoacqaEnp8tAI",

    # Yellow cover cards
    "10": "CAADAgADp2UAAk2SaEmoCVHGcgdTtQI",
    "11": "CAADAgADoF4AAou7aElRVaTkOU18WwI",
    "12": "CAADAgADF1QAAgOxaEnb8upzNW4xgAI",
    "13": "CAADAgADgFkAAqh_aUngp6xP4JXcPQI",
    "14": "CAADAgADzVcAAsLmaUm-PHHdJDTxEQI",
    "15": "CAADAgADYWMAArRoaElOqOjVhm_kvgI",
    "16": "CAADAgADM2IAApHRaUnqGYs6DsRCwgI",
    "17": "CAADAgADTVoAAuGzaEmUrXjZTeRAiQI",
    "18": "CAADAgADL2QAAnLiaEnovkFJevgaFwI",
    "19": "CAADAgADi1kAAtnsaElCTVZiHuCa8QI",


    # Green cover cards
    "20": "CAADAgADLWcAArqXaEm4wBY2S8eqpAI",
    "21": "CAADAgAD9GAAAsSBaUkUM8BL6ccUKAI",
    "22": "CAADAgADzmUAAp--aEn9498Mhr_kSAI",
    "23": "CAADAgADFl4AAitIaUnjPMUFFd7KTAI",
    "24": "CAADAgADQFkAAl2AaUkyanMOPXbRLwI",
    "25": "CAADAgADnm0AAr-0aUkZn781zzosUAI",
    "26": "CAADAgADA1kAAsJoaUnzTX_u2fW5FwI",
    "27": "CAADAgADqF4AAkXsaUmJOP0m7XXC9wI",
    "28": "CAADAgADEGIAAnoHaEmM2XXh-W9ZqgI",
    "29": "CAADAgADFloAAjd3aUmdabV4t7JBpAI",

    # Blue sticker cards
    "30": "CAADAgADPWcAAv_LaUmTh1_yMkS96gI",
    "31": "CAADAgADVlsAAjEnYElGUTtPoAGXCgI",
    "32": "CAADAgADLWEAArjYaUmSjSAi3PRIUgI",
    "33": "CAADAgADeF4AAt0YaEn8A4f2u3o-AwI",
    "34": "CAADAgADaF0AAvxVaEnuW8vbG1ldRQI",
    "35": "CAADAgADP1oAAjOtaUneHfpcA9NPtgI",
    "36": "CAADAgADCl4AArAUaEmPRoVJZ1ERnAI",
    "37": "CAADAgADhl4AAjFDaEkhBGKU4DFu1gI",
    "38": "CAADAgADrGYAAup_aEmJr4vqhx3GmgI",
    "39": "CAADAgADNmMAAoqYaUnvt34qaMi7qAI",
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
skip_pattern = re.compile(r"skip([0-5])(\d):\d")
take_pattern = re.compile(r"take([0-5])(\d):\d")
reverse_pattern = re.compile(r"reverse([0-5]):\d")
number_pattern = re.compile(r"([0-5])(\d):\d")

def to_sticker_id(card: BaseCard) -> str:
    """Преобразует карту в строковый ID для стикера."""
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

def to_str(card: BaseCard) -> str:
    """Превращает карту в строковый ID."""
    if isinstance(card, NumberCard):
        return f"{card.color.value}{card.value}" # 00 .. # 59
    elif isinstance(card, TurnCard):
        return f"skip{card.color.value}{card.value}"
    elif isinstance(card, ReverseCard):
        return f"reverse{card.color.value}"
    elif isinstance(card, TakeCard):
        return f"take{card.color.value}{card.value}"
    elif isinstance(card, ChooseColorCard):
        return "choose_color"
    elif isinstance(card, TakeFourCard):
        return "take_four"

def from_str(card_str: str) -> BaseCard:
    """Превращает строку карты в действительный экземпляр."""
    if re.match(r"choose_color:\d", card_str):
        return ChooseColorCard()

    elif re.match(r"take_four:\d", card_str):
        return TakeFourCard()

    match = skip_pattern.match(card_str)
    if match is not None:
        groups = match.groups()
        return TurnCard(CardColor(int(groups[0])), int(groups[1]))

    match = take_pattern.match(card_str)
    if match is not None:
        groups = match.groups()
        return TakeCard(CardColor(int(groups[0])), int(groups[1]))

    match = reverse_pattern.match(card_str)
    if match is not None:
        groups = match.groups()
        return ReverseCard(CardColor(int(groups[0])))

    match = number_pattern.match(card_str)
    if match is not None:
        groups = match.groups()
        return NumberCard(CardColor(int(groups[0])), int(groups[1]))
