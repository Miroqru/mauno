"""Общие клавиатуры бота.

В тои числе клавиатура для Inline Query.
"""

from collections.abc import Iterator, Sequence

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
)

from mau.enums import CardType, GameState
from mau.game.game import UnoGame
from mau.game.player import Player
from mau.game.rules import GameRules, Rule
from maubot.config import config, stickers
from maubot.messages import get_room_status

# Когда кто-то пробует использовать inline режим бота без активной комнаты
NO_GAME_QUERY = InlineQueryResultArticle(
    id="nogame",
    title="В чате ещё нет игровой комнаты",
    input_message_content=InputTextMessageContent(
        message_text=(
            "☕ Сейчас никто не играет.\n\n"
            "Используйте /game для создания новой комнаты.\n"
            "А после воспользуйтесь /join чтобы присоединиться к комнате. "
        )
    ),
)


SHOTGUN_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Взять 🃏", callback_data="take"),
            InlineKeyboardButton(text="🔫 Выстрелить", callback_data="shot"),
        ]
    ]
)

SELECT_COLOR = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❤️", callback_data="color:0"),
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


def get_room_markup(game: UnoGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой.

    Позволяет начать игру и присоединиться к ней.
    А также открыть клавиатуру для настройки игровых правил.
    """
    buttons = [
        [
            InlineKeyboardButton(text="🪄 Правила", callback_data="room_rules"),
            InlineKeyboardButton(text="🃏 Колода", callback_data="deck_edit"),
            InlineKeyboardButton(text="☕ Зайти", callback_data="join"),
        ]
    ]
    if len(game.pm) >= config.min_players:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🎮 Начать игру", callback_data="start_game"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Собираем Inline query с колодой пользователя
# ============================================

_COLOR_INFO = (
    (0, "Красный", "❤️"),
    (1, "Жёлтый", "💛"),
    (2, "Зелёный", "💚"),
    (3, "Синий", "💙"),
)


def get_hand_cards(player: Player) -> Iterator[InlineQueryResultCachedSticker]:
    """Возвращает карты пользователя из руки."""
    player_cards = player.cover_cards()
    for i, cover_card in enumerate(player_cards.cover):
        yield InlineQueryResultCachedSticker(
            id=f"{cover_card.to_str()}:{i}",
            sticker_file_id=stickers.normal[cover_card.to_str()],
        )

    for i, cover_card in enumerate(player_cards.uncover):
        yield InlineQueryResultCachedSticker(
            id=f"status:{i}",
            sticker_file_id=stickers.not_playable[cover_card.to_str()],
            input_message_content=InputTextMessageContent(
                message_text=get_room_status(player.game)
            ),
        )


def _add_sticker(
    id: str, sticker: str, message: str
) -> InlineQueryResultCachedSticker:
    return InlineQueryResultCachedSticker(
        id=id,
        sticker_file_id=sticker,
        input_message_content=InputTextMessageContent(message_text=message),
    )


def get_hand_query(
    player: Player,
) -> Sequence[InlineQueryResultCachedSticker | InlineQueryResultArticle]:
    """Возвращает основную игровую клавиатуру."""
    result = []
    if player.game.state == GameState.TAKE:
        result = [
            _add_sticker("next", stickers.options.next_turn, "👀 Пропускаю")
        ]
    elif player == player.game.player:
        result = [_add_sticker("take", stickers.options.draw, "👀 Беру карту")]

    if (
        player.game.deck.top.card_type == CardType.TAKE_FOUR
        and player.game.take_counter
    ):
        result.append(
            _add_sticker(
                "bluff",
                stickers.options.bluff,
                "🍷 Ты блефуешь, показывай карты!",
            )
        )

    result.extend(get_hand_cards(player))
    return result


# Настройки игровой комнаты
# =========================


def get_rules_markup(game_rules: GameRules) -> InlineKeyboardMarkup:
    """Генерирует кнопки на основе правил игры."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{'🌟' if rule[1] else ''}{rule[0]}",
                    callback_data=f"rule:{i}",
                )
            ]
            for i, rule in enumerate(game_rules.iter_rules())
        ]
    )


def select_player_markup(game: "UnoGame") -> InlineKeyboardMarkup:
    """Клавиатура для выбора игрока.

    Отображает имя игрока и сколько у него сейчас карт.
    """
    res = []
    for i, pl in game.pm.iter_others():
        res.append(
            [
                InlineKeyboardButton(
                    # TODO: Ну когда там username
                    text=f"{pl.name} ({len(pl.hand)} 🃏)",
                    callback_data=f"select_player:{i}",
                )
            ]
        )

    if game.rules.twist_hand_pass.status:
        res.append(
            [InlineKeyboardButton(text="🍷 Пропустить", callback_data="next")]
        )

    return InlineKeyboardMarkup(inline_keyboard=res)
