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
from maubot.messages import get_room_status
from maubot.uno.card import CardType, TakeFourCard
from maubot.uno.enums import GameState
from maubot.uno.game import RULES, GameRules, UnoGame

# Кнопка для совершения хода игроком
# Будет прикрепляться к игровым сообщениям
TURN_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="Сделать ход",
        switch_inline_query_current_chat=""
    )
]])

SELECT_PLAYER_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="Выбрать игрока",
        switch_inline_query_current_chat=""
    )
]])


# Используется при выборе цвета для специальных карт
COLOR_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="❤️", callback_data="color:0"),
    InlineKeyboardButton(text="💛", callback_data="color:1"),
    InlineKeyboardButton(text="💚", callback_data="color:2"),
    InlineKeyboardButton(text="💙", callback_data="color:3")
]])

def get_room_markup(game: UnoGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой."""
    buttons = [[
        InlineKeyboardButton(text="⚙️ Настройки",
            callback_data="room_settings"
        ),
        InlineKeyboardButton(text="☕ Зайти", callback_data="join")
    ]]
    if len(game.players) >= config.min_players:
        buttons.append([InlineKeyboardButton(text="🃏 Начать игру",
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
            message_text=get_room_status(player.game)
        ),
    ))
    return result

def select_player_query(player, add_pass_button: bool = False) -> list:
    """Клавиатура для выбора игрока."""
    result = []

    for i, pl in enumerate(player.game.players):
        if i == player.game.current_player:
            continue

        result.append(InlineQueryResultArticle(
            id=f"select_player:{i}",
            title=f"{pl.user.first_name} ({len(pl.hand)} карт)",
            input_message_content=InputTextMessageContent(message_text=(
                f"🔪 Я выбираю {pl.user.first_name}."
            ))
        ))

    if add_pass_button:
        result.append(InlineQueryResultArticle(
            id="pass",
            title="Пропустить ход",
            input_message_content=InputTextMessageContent(message_text=(
                "🍷 В этот раз я оставлю всё как есть."
            ))
        ))

    return result


def get_hand_cards(player) -> Iterator:
    """Возвращает карты пользователя из руки."""
    player_cards = player.get_cover_cards()
    for i, cover_card in enumerate(player_cards.cover):
        if cover_card.card_type in (CardType.TAKE_FOUR, CardType.CHOOSE_COLOR):
            yield InlineQueryResultCachedSticker(
                id=f"{stickers.to_str(cover_card)}:{i}",
                sticker_file_id=stickers.NORMAL[
                    stickers.to_sticker_id(cover_card)
                ],
                reply_markup=COLOR_MARKUP
            )
        elif cover_card.value == 7 and player.game.rules.twist_hand:
            yield InlineQueryResultCachedSticker(
                id=f"{stickers.to_str(cover_card)}:{i}",
                sticker_file_id=stickers.NORMAL[
                    stickers.to_sticker_id(cover_card)
                ],
                reply_markup=SELECT_PLAYER_MARKUP
            )
        else:
            yield InlineQueryResultCachedSticker(
                id=f"{stickers.to_str(cover_card)}:{i}",
                sticker_file_id=stickers.NORMAL[
                    stickers.to_sticker_id(cover_card)
                ]
            )

    for i, cover_card in enumerate(player_cards.uncover):
        yield InlineQueryResultCachedSticker(
            id=f"status:{i}",
            sticker_file_id=stickers.NOT_PLAYABLE[
                stickers.to_sticker_id(cover_card)
            ],
            input_message_content=InputTextMessageContent(
                message_text=get_room_status(player.game)
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
                message_text=get_room_status(player.game)
            )
        )


def get_hand_query(player) -> list:
    """Возвращает основную игровую клавиатуру."""
    # Если игрой сейчас не играет, то и действий никаких у него нету
    if not player.is_current:
        return get_all_hand_cards(player)

    if player.game.state == GameState.CHOOSE_COLOR:
        return get_color_query(player)

    if player.game.state == GameState.TWIST_HAND:
        return select_player_query(player)

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
            message_text=get_room_status(player.game)
    )))

    return result


# Настройки игровой комнаты
# =========================

def get_settings_markup(game_rules: GameRules) -> InlineKeyboardMarkup:
    """Клавиатура для управления настройками комнаты."""
    buttons = []
    for rule in RULES:
        status = getattr(game_rules, rule.key, False)
        if status:
            status_sim = "🌟"
        else:
            status_sim = ""

        buttons.append([InlineKeyboardButton(
            text=f"{status_sim}{rule.name}",
            callback_data=f"set:{rule.key}:{not status}"
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
