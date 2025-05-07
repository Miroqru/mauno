"""Общие клавиатуры бота.

В тои числе клавиатура для Inline Query.
"""

from collections.abc import Iterator

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.types import InlineQueryResultArticle as InlineArticle
from aiogram.types import InlineQueryResultCachedSticker as InlineSticker
from aiogram.types import InputTextMessageContent as InputText

from mau.enums import CardType, GameState
from mau.game.game import UnoGame
from mau.game.player import Player
from mau.game.player_manager import PlayerManager
from maubot.config import config, stickers
from maubot.messages import game_status

# Когда кто-то пробует использовать inline режим бота без активной комнаты
NO_GAME_QUERY = InlineArticle(
    id="nogame",
    title="В чате ещё нет игровой комнаты",
    input_message_content=InputText(
        message_text=(
            "☕ Сейчас никто не играет.\n\n"
            "Используйте /game для создания новой комнаты.\n"
            "А после воспользуйтесь /join чтобы присоединиться к комнате. "
        )
    ),
)


SHOTGUN_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Взять 🃏", callback_data="shot_take"),
            InlineKeyboardButton(text="🔫 Выстрелить", callback_data="shot"),
        ]
    ]
)

SELECT_COLOR = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🩷", callback_data="color:0"),
            InlineKeyboardButton(text="💛", callback_data="color:1"),
            InlineKeyboardButton(text="💚", callback_data="color:2"),
            InlineKeyboardButton(text="💙", callback_data="color:3"),
        ],
        [
            InlineKeyboardButton(
                text="🃏 Ваши карты", switch_inline_query_current_chat=""
            )
        ],
    ]
)

NEW_GAME_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🍪 Новая игра", callback_data="new_game")]
    ]
)


def hand_query(player: Player) -> Iterator[InlineSticker]:
    """Возвращает основную клавиатуру с игровыми действиями."""
    player_cards = player.cover_cards()
    for i, cover_card in enumerate(player_cards.cover):
        yield InlineSticker(
            id=f"{cover_card.to_str()}:{i}",
            sticker_file_id=stickers.normal[cover_card.to_str()],
        )

    for i, cover_card in enumerate(player_cards.uncover):
        yield InlineSticker(
            id=f"status:{i}",
            sticker_file_id=stickers.not_playable[cover_card.to_str()],
            input_message_content=InputText(
                message_text=game_status(player.game)
            ),
        )


# Inline клавиатура
# =================


def select_player(pm: PlayerManager, skip_button: bool) -> InlineKeyboardMarkup:
    """Клавиатура для выбора игрока.

    Содержит имя игрока и сколько у него сейчас карт.
    """
    res = [
        [
            InlineKeyboardButton(
                text=f"{pl.name} ({len(pl.hand)} 🃏)",
                callback_data=f"select_player:{pl.user_id}",
            )
        ]
        for i, pl in pm.iter_others()
    ]

    if skip_button:
        res.append(
            [InlineKeyboardButton(text="🍷 Пропустить", callback_data="next")]
        )

    return InlineKeyboardMarkup(inline_keyboard=res)


def lobby_markup(game: UnoGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой.

    Позволяет начать игру и присоединиться к ней.
    А также открыть клавиатуру для настройки игровых правил.
    """
    buttons = [
        [
            InlineKeyboardButton(text="🪄 Правила", callback_data="room_rules"),
            InlineKeyboardButton(text="🃏 Колода", callback_data="deck_edit"),
        ],
        [
            InlineKeyboardButton(text="☕ Зайти", callback_data="join"),
        ],
    ]
    if len(game.pm) >= config.min_players:
        buttons[0].append(
            InlineKeyboardButton(
                text="🎮 Начать игру", callback_data="start_game"
            )
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def turn_markup(game: UnoGame) -> InlineKeyboardMarkup:
    """Клавиатура для хода."""
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="🎮 Разыграть 🃏",
                switch_inline_query_current_chat="",
            )
        ]
    ]

    if game.state == GameState.TAKE:
        inline_keyboard[0].append(
            InlineKeyboardButton(text="🍓 завершить", callback_data="next")
        )

    else:
        inline_keyboard[0].append(
            InlineKeyboardButton(text="🃏 взять", callback_data="take")
        )

    if game.deck.top.card_type == CardType.TAKE_FOUR and game.take_counter:
        inline_keyboard[0].append(
            InlineKeyboardButton(text="🍷 блефуешь", callback_data="bluff")
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
