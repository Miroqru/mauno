"""Общие клавиатуры бота.

В тои числе клавиатура для Inline Query.
"""

from maubot import stickers
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultCachedSticker
)

# Кнопка для совершения хода игроком
# Будет прикрепляться к игровым сообщениям
TURN_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="Сделать ход",
        switch_inline_query_current_chat=""
    )
]])

# Меню выбора режима игры
# Помогает удобнее применить настройки игровых правил
# Тут есть только два пункта: классика и дикий режим
# TODO: Переписать под функцию, после это может понадобиться
SELECT_GAME_QUERY = [
    InlineQueryResultArticle(
        id="mode_classic",
        title="🎻 Классический режим",
        input_message_content=InputTextMessageContent(message_text=(
            "🎻 <b>Классический режим</b>:\n"
            "Уже привычная вам игра с набором из 108 карт."
        ))
    ),
    InlineQueryResultArticle(
        id="mode_wild",
        title="🐉 Дикий режим",
        input_message_content=InputTextMessageContent(message_text=(
            "🐉 <b>Дикий режим</b>:\n"
            "Более динамичный вариант игры.\n"
            "По 4 набора числовых карт 0-5 и специальных карт.\n"
            "А также по 6 чёрных карт чтобы игра была веселее."
        ))
    )
]

NO_GAME_QUERY = [
    InlineQueryResultArticle(
        id="nogame",
        title="В чатике ещё нет комнаты",
        input_message_content=InputTextMessageContent(message_text=(
            "Сейчас никто не играет.\n\n"
            "Используйте /game для создания новой комнаты.\n"
            "А после воспользуйтесь командой /join чтобы присоединиться. "
        ))
    )
]


def get_hand_query(player) -> list:
    result = [
        InlineQueryResultCachedSticker(
            id="draw",
            sticker_file_id=stickers.OPTIONS.draw,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Кусь")
            ]])
        )
    ]

    return result