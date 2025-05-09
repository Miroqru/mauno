"""Общие клавиатуры бота.

В тои числе клавиатура для Inline Query.
"""

from collections.abc import Iterator

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.types import InlineQueryResultArticle as InlineArticle
from aiogram.types import InlineQueryResultPhoto as InlinePhoto
from aiogram.types import InputTextMessageContent as InputText

from mau.deck.behavior import WildTakeBehavior
from mau.enums import CardColor, GameState
from mau.game.game import UnoGame
from mau.game.player import Player
from mau.game.player_manager import PlayerManager
from maubot.config import config
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
            InlineKeyboardButton(
                text="❤️", callback_data=f"color:{CardColor.RED}"
            ),
            InlineKeyboardButton(
                text="💛", callback_data=f"color:{CardColor.YELLOW}"
            ),
            InlineKeyboardButton(
                text="💚", callback_data=f"color:{CardColor.GREEN}"
            ),
            InlineKeyboardButton(
                text="💙", callback_data=f"color:{CardColor.CYAN}"
            ),
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


def hand_query(player: Player) -> Iterator[InlinePhoto]:
    """Возвращает основную клавиатуру с игровыми действиями."""
    player_cards = player.cover_cards()
    for i, card in enumerate(player_cards.cover):
        yield InlinePhoto(
            id=f"{card.pack()}:{i}",
            photo_url=f"https://mau.miroq.ru/card/{card.pack()}/false",
            thumbnail_url=f"https://mau.miroq.ru/card/{card.pack()}/false",
            photo_width=64,
            photo_height=128,
            description=card.pack(),
        )

    for i, card in enumerate(player_cards.uncover):
        yield InlinePhoto(
            id=f"status:{i}",
            photo_url=f"https://mau.miroq.ru/card/{card.pack()}/true",
            thumbnail_url=f"https://mau.miroq.ru/card/{card.pack()}/true",
            input_message_content=InputText(
                message_text=game_status(player.game),
            ),
            photo_width=64,
            photo_height=128,
            description=card.pack(),
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

    if (
        isinstance(game.deck.top.behavior, WildTakeBehavior)
        and game.take_counter
    ):
        inline_keyboard[0].append(
            InlineKeyboardButton(text="🍷 блефуешь", callback_data="bluff")
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
