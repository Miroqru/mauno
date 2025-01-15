"""Набор стикеров UNO.

Хранит в себе таблицу всех стикеров из стикер пака.
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
    "color": "CAADAgADPHsAAiaIEEo3PH_1_hJiAgI",
    "take_four": "CAADAgAD4VIAAtKFGUraSw7N0M3cdQI",

    "take0": "CAADAgADnVUAAvgdGErG3_gKpp8jnwI",
    "take1": "CAADAgADFV8AAheZGUqoCJetzCx0FgI",
    "take2": "CAADAgAD-18AAoorEEpOkXxhbOXNCQI",
    "take3": "CAADAgADDlcAAszHGEruHxf6-SMqTAI",

    "reverse0": "CAADAgAD_lsAAjvWGUoLvRT6qdCvQgI",
    "reverse1": "CAADAgADKVwAAuTYGUr7NN0nPKXkVwI",
    "reverse2": "CAADAgADL2AAAr_4GUpxfQzKTSn8pwI",
    "reverse3": "CAADAgADa2IAAiHNEEreGC52-rt7YwI",

    "skip0": "CAADAgADN1sAAtg4GEpjUbLGSlPd4QI",
    "skip1": "CAADAgADtlwAAiMfGUp_gg84Dt6P0wI",
    "skip2": "CAADAgADQ2MAAtCSEEpw-HUIqKmyPgI",
    "skip3": "CAADAgADc1cAAsx0GUp0W_o9dNpQuQI",

    # Red number cards
    "00": "CAADAgADOmIAAuNeGErlPISFevq19wI",
    "01": "CAADAgADGG0AAvtbEUp645xI3UYcywI",
    "02": "CAADAgADNV4AAgGRGEoW2yobjO6_WQI",
    "03": "CAADAgADmmAAAkJpGUqTTg0Uv0xOIgI",
    "04": "CAADAgAD_2EAAjn5GEqGCPyLTfH37gI",
    "05": "CAADAgADZ2MAAq0KEUpQpP6csbO4pAI",
    "06": "CAADAgADi1cAAgnnGEpS1c3PdDgYTgI",
    "07": "CAADAgAD9FUAAv-OGEpJ3Z1Z45z_5QI",
    "08": "CAADAgADzFwAApocGEq-KOcFXZxyiAI",
    "09": "CAADAgAD8WEAAtJrEEqfCfRoWkjzIgI",

    # Yellow number cards
    "10": "CAADAgADrlsAAocrGErWJLYBSmFoGwI",
    "11": "CAADAgADnFcAAuJyGErFTIuG_L1ZwAI",
    "12": "CAADAgADY2gAAmygEEqEg-gCwiU_4gI",
    "13": "CAADAgADsl8AAtXBGUrNbif0q8l1-AI",
    "14": "CAADAgADJVMAAjokGUpyWydWzukMOQI",
    "15": "CAADAgADU2YAAhD7EUrMQtTN1Lj55QI",
    "16": "CAADAgADSFgAAl_QGEraWQ-nxarmggI",
    "17": "CAADAgADYFUAAnKFGUonScuLHzE--QI",
    "18": "CAADAgADC1oAAp64GEpi306cxS87OAI",
    "19": "CAADAgADumAAAmgfEEqBFVYfNbklPwI",

    # Green number cards
    "20": "CAADAgADsVsAAkmoGErG-B_sF6QOEQI",
    "21": "CAADAgADFZIAAiCrEEpEPIB6RRJ0YAI",
    "22": "CAADAgADoFcAAqVXGUrTPjeVI9ImAAEC",
    "23": "CAADAgADQVsAAsEAARlK2AexgwTPCjoC",
    "24": "CAADAgADCVgAAr5BGUp--URzI__SDQI",
    "25": "CAADAgADVl8AAh1yGEo5epBsxE2N-AI",
    "26": "CAADAgADWV4AAs6fEEoNTVqn_47HBQI",
    "27": "CAADAgAD_FYAAlziGUoIHB0NriUugwI",
    "28": "CAADAgADgWUAAlG3EEq3mnUNHX4b3wI",
    "29": "CAADAgAD-FQAAhYRGUq6RXipo41hcQI",

    # Blue number cards
    "30": "CAADAgADu2AAAqHqGEpu5u3-WrVRkQI",
    "31": "CAADAgADN1kAAoI3GUrmW2B1o9RC1wI",
    "32": "CAADAgADlmUAAnpCEErUUjwHvTP3YwI",
    "33": "CAADAgADUWMAAn0mGUqd6LqmRuaCPgI",
    "34": "CAADAgADa10AAkJcGEq3yvpEyvPjbgI",
    "35": "CAADAgADe10AAldHGUpjbmjHYDeV2QI",
    "36": "CAADAgADhmAAAgTWGEqiDMNbcXWBjgI",
    "37": "CAADAgADzmgAAicDEUq5fpJVMp-EfAI",
    "38": "CAADAgADulYAAoRoGUpepgXpIvtkggI",
    "39": "CAADAgADClUAAg5AGUoTCkMJPPvrngI",
}

NOT_PLAYABLE = {
    "color": "CAADAgADJGEAAnEeGUoVBvnlTBYG2AI",
    "take_four": "CAADAgADd1UAAmPXGUpHi5F59z2RjAI",

    "take0": "CAADAgADnVoAAtBlGEocOLZl0DtzzQI",
    "take1": "CAADAgADkmAAAnbiEEphvXVuLmsnCgI",
    "take2": "CAADAgADCVsAAqdvGUrWr2UAARZtAAGUAg",
    "take3": "CAADAgAD7loAAsw4GEonEPlnzQuQmwI",

    "reverse0": "CAADAgAD9VEAAvYOGUrw7842otILNAI",
    "reverse1": "CAADAgADaGIAAg01GUrruSTxSWVN3QI",
    "reverse2": "CAADAgADflMAAltHGErDzleE2WTy_gI",
    "reverse3": "CAADAgADok0AAjPkGEpWl-xL_xzmkgI",

    "skip0": "CAADAgADTF0AAr8TGEqfyKyWH_8lKAI",
    "skip1": "CAADAgADfWEAAnf6EEq1r3zdmFWp6QI",
    "skip2": "CAADAgADslgAArcCGUrIprPCAmQPsgI",
    "skip3": "CAADAgAD-1MAAlxQGErshcIYTIYF5QI",

    # Red number cards
    "00": "CAADAgADGVsAAn7FGEomnhx2TFdljQI",
    "01": "CAADAgADf2gAAvJ6EEqv4nu3QaoKtgI",
    "02": "CAADAgAD-lkAAsrsEEpWL_-_p3ELlAI",
    "03": "CAADAgADkWUAArH9GEqmviv0X6Rg_wI",
    "04": "CAADAgADk2gAAo8EEUrhoJIxT74rqAI",
    "05": "CAADAgAD0l4AAriNGEp1TcEWlbraZQI",
    "06": "CAADAgADBV4AAmW3EUoPchSVWeumPgI",
    "07": "CAADAgADxVgAAqvRGErzQqC5TLaQGgI",
    "08": "CAADAgADvloAAikWGEoCZPcNcnCX0wI",
    "09": "CAADAgADHF0AAp5hGEohvhqt8yZ0GAI",

    # Yellow cover cards
    "10": "CAADAgADVGEAArhrEEr5Y59EePdtugI",
    "11": "CAADAgADelsAAgS2GEr-TfvXhmpDDAI",
    "12": "CAADAgADLmIAAlgyEUoff8xydANDUQI",
    "13": "CAADAgADTGQAAhrwGEof694hB2MrzwI",
    "14": "CAADAgADdFwAAotHGEodJYghFY3R-QI",
    "15": "CAADAgADt2EAAuk-EEqMZ4bDug3HsgI",
    "16": "CAADAgADkmUAAosREEofIE2w-zM6OAI",
    "17": "CAADAgADlVgAAqJKGEpNtXJoky_WFAI",
    "18": "CAADAgADvlYAAiHzGUrt4g16i437MwI",
    "19": "CAADAgAD1VMAApBrGUpThaFe58GQCgI",


    # Green cover cards
    "20": "CAADAgADG14AAjRNEEp_z2Vazeu7lwI",
    "21": "CAADAgADBV4AAq_tEEoLIjGkp7aPYwI",
    "22": "CAADAgAD4XEAAmVYGEqauroYI5nMmAI",
    "23": "CAADAgADW2IAAuETGEqFlt_ZKt-2qwI",
    "24": "CAADAgADjV0AAjV_GEpN3VdGKzwlbQI",
    "25": "CAADAgADXmAAAqkKGUoAAUdDT2Wg_i8C",
    "26": "CAADAgADyVgAAjNmGUoknhMcwEReowI",
    "27": "CAADAgADOVQAArMaGEoxBhhl2F56QAI",
    "28": "CAADAgAD2msAAueEGUpCFBLLgjMI4gI",
    "29": "CAADAgAD61cAAg3ZGEr-YMKj5N7_SAI",

    # Blue sticker cards
    "30": "CAADAgADZFgAAh0FGUpT05JzSMNNMQI",
    "31": "CAADAgADoFMAAjc1GEo_7oRbdMbkkgI",
    "32": "CAADAgADflwAAkxsGUrGRxI9sw56TAI",
    "33": "CAADAgADpGEAAkmeEUogAodi_jRniAI",
    "34": "CAADAgADC1QAAhxRGUpb75YcFhkonQI",
    "35": "CAADAgADwVMAAskiGEoLfnEZnnxflwI",
    "36": "CAADAgADZlsAAvjiGUqeP8xiliaZvAI",
    "37": "CAADAgADFlkAAs0bGEqrMpeiNRD2MgI",
    "38": "CAADAgADnmEAAjOAGEqYtL4NhKaZ3AI",
    "39": "CAADAgAD_VcAAmjxGUq2J9fT5I6CrgI",
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
    bluff = "CAADAgAD3l8AAmhnGUpEc9H33kKNogI",
    draw = "CAADAgAD01UAAhAZGEofZ5ztvSiLtAI",
    info = "CAADAgAD72EAAmV9GUrFGV1GnASDHwI",
    next_turn = "CAADAgADZ2IAAouNEUpzqTKGgvjDKAI",
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
