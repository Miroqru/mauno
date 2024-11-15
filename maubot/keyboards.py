"""Общие клавиатуры бота.

В тои числе клавиатура для Inline Query.
"""

from typing import Iterator

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
)

from maubot import stickers
from maubot.config import config
from maubot.messages import game_status
from maubot.uno.card import TakeFourCard
from maubot.uno.game import UnoGame

# Кнопка для совершения хода игроком
# Будет прикрепляться к игровым сообщениям
TURN_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="Сделать ход",
        switch_inline_query_current_chat=""
    )
]])

def get_room_markup(game: UnoGame) -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(text="Выбрать режим",
            switch_inline_query_current_chat=""
        ),
        InlineKeyboardButton(text="Зайти", callback_data="join")
    ]]
    if len(game.players) >= config.min_players:
        buttons.append([InlineKeyboardButton(text="Начать игру",
            callback_data="start_game"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Меню выбора режима игры
# Помогает удобнее применить настройки игровых правил
# Тут есть только два пункта: классика и дикий режим
# TODO: Переписать под функцию, после это может понадобиться
SELECT_GAME_QUERY = [
    InlineQueryResultArticle(
        id="mode:classic",
        title="🎻 Классический режим",
        input_message_content=InputTextMessageContent(message_text=(
            "🎻 <b>Классический режим</b>:\n"
            "Уже привычная вам игра с набором из 108 карт."
        ))
    ),
    InlineQueryResultArticle(
        id="mode:wild",
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
        title="В чате ещё нет комнаты",
        input_message_content=InputTextMessageContent(message_text=(
            "Сейчас никто не играет.\n\n"
            "Используйте /game для создания новой комнаты.\n"
            "А после воспользуйтесь командой /join чтобы присоединиться. "
        ))
    )
]

# Собираем Inline query с колодой пользователя
# ============================================

_COLOR_INFO = (
    (0, "Красный", "❤️"),
    (1, "Жёлтый", "💛"),
    (2, "Зелёный", "💚"),
    (3, "Синий", "💙"),
)

def get_color_query(player) -> list:
    """Клавиатура для выбора следующего цвета."""
    result = [
        InlineQueryResultArticle(
            id=f"color:{i}",
            title=f"Выбираю {name}",
            input_message_content=InputTextMessageContent(message_text=(
                f"Я выбираю {sim}{name}"
            ))
        )
        for i, name, sim in _COLOR_INFO
    ]
    result.append(InlineQueryResultArticle(
        id="status",
        title="Ваши карты (жмяк для статуса комнаты):",
        description=", ".join([str(card) for card in player.hand]),
        input_message_content=InputTextMessageContent(
            message_text=game_status(player.game)
        ),
    ))
    return result

def get_hand_cards(player) -> Iterator:
    """Возвращает карты пользователя из руки."""
    player_cards = player.get_cover_cards()
    for i, cover_card in enumerate(player_cards.cover):
        yield InlineQueryResultCachedSticker(
            id=f"{stickers.to_str(cover_card)}:{i}",
            sticker_file_id=stickers.NORMAL[stickers.to_sticker_id(cover_card)]
        )

    for i, cover_card in enumerate(player_cards.uncover):
        yield InlineQueryResultCachedSticker(
            id=f"status:{i}",
            sticker_file_id=stickers.NOT_PLAYABLE[
                stickers.to_sticker_id(cover_card)
            ],
            input_message_content=InputTextMessageContent(
                message_text=game_status(player.game)
            )
        )

def get_all_hand_cards(player):
    """Получает все карты пользователя."""
    for i, cover_card in enumerate(player.hand):
        yield InlineQueryResultCachedSticker(
            id=f"status:{i}",
            sticker_file_id=stickers.NOT_PLAYABLE[
                stickers.to_sticker_id(cover_card)
            ],
            input_message_content=InputTextMessageContent(
                message_text=game_status(player.game)
            )
        )


def get_hand_query(player) -> list:
    """Возвращает основную игровую клавиатуру."""
    # Если игрой сейчас не играет, то и действий никаких у него нету
    if not player.is_current:
        return get_all_hand_cards(player)

    if player.game.choose_color_flag:
        return get_color_query(player)

    if player.took_card:
        result = [InlineQueryResultCachedSticker(
            id="pass",
            sticker_file_id=stickers.OPTIONS.next_turn,
            input_message_content=InputTextMessageContent(message_text=(
                "Пропускаю."
            )))
        ]
    else:
        if player.game.take_counter:
            take_message = f"🃏 Беру {player.game.take_counter} карт."
        else:
            take_message = "🃏 Беру карту."

        result = [InlineQueryResultCachedSticker(
            id="take",
            sticker_file_id=stickers.OPTIONS.draw,
            input_message_content=InputTextMessageContent(message_text=(
                take_message
            )))
        ]

    if (isinstance(player.game.deck.top, TakeFourCard)
        and player.game.take_counter
    ):
        result.append(InlineQueryResultCachedSticker(
            id="bluff",
            sticker_file_id=stickers.OPTIONS.bluff,
            input_message_content=InputTextMessageContent(message_text=(
                "Я оспорю твой блеф!"
            ))
        ))

    # Карты из руки уже сортированы, остаётся только их добавить
    for card_query in get_hand_cards(player):
        result.append(card_query)

    # Явное отображение статуса игры
    result.append(InlineQueryResultCachedSticker(
        id="status",
        sticker_file_id=stickers.OPTIONS.info,
        input_message_content=InputTextMessageContent(
            message_text=game_status(player.game)
    )))

    return result
