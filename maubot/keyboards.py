"""Общие клавиатуры бота.

В тои числе клавиатура для Inline Query.
"""

from collections.abc import Iterator

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
)

from mau.card import TakeFourCard
from mau.enums import GameState
from mau.game import RULES, GameRules, UnoGame
from mau.player import Player
from maubot.config import config, stickers
from maubot.messages import get_room_status, take_cards_message

# Когда кто-то пробует использовать inline режим бота без активной комнаты
NO_GAME_QUERY = [
    InlineQueryResultArticle(
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
]


def get_room_markup(game: UnoGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой.

    Позволяет начать игру и присоединиться к ней.
    А также открыть клавиатуру для настройки игровых правил.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="⚙️ Правила", callback_data="room_settings"
            ),
            InlineKeyboardButton(text="☕ Зайти", callback_data="join"),
        ]
    ]
    if len(game.players) >= config.min_players:
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


def get_color_query(player: Player) -> list[InlineQueryResultArticle]:
    """Клавиатура для выбора следующего цвета."""
    result = [
        InlineQueryResultArticle(
            id=f"color:{i}",
            title=f"Выбрать {name}",
            input_message_content=InputTextMessageContent(
                message_text=(f"🎨 Я выбираю.. {sim}")
            ),
        )
        for i, name, sim in _COLOR_INFO
    ]
    result.append(
        InlineQueryResultArticle(
            id="status",
            title="Ваши карты (жмяк для статуса комнаты):",
            description=", ".join([str(card) for card in player.hand]),
            input_message_content=InputTextMessageContent(
                message_text=get_room_status(player.game)
            ),
        )
    )
    return result


# TODO: А может убрать эту функцию совсем
def select_player_query(
    player: Player, add_pass_button: bool = False
) -> list[InlineQueryResultArticle]:
    """Клавиатура для выбора игрока."""
    result = []

    for i, pl in enumerate(player.game.players):
        if i == player.game.current_player:
            continue

        result.append(
            InlineQueryResultArticle(
                id=f"select_player:{i}",
                title=f"{pl.name} ({len(pl.hand)} карт)",
                input_message_content=InputTextMessageContent(
                    message_text=(f"🔪 Я <b>выбираю</b> {pl.name}.")
                ),
            )
        )

    # TODO: Этой кнопкой так никто и не воспользовался, блин
    if add_pass_button:
        result.append(
            InlineQueryResultArticle(
                id="pass",
                title="Пропустить ход",
                input_message_content=InputTextMessageContent(
                    message_text=("🍷 В этот раз я оставлю всё как есть.")
                ),
            )
        )

    return result


def get_hand_cards(player: Player) -> Iterator[InlineQueryResultCachedSticker]:
    """Возвращает карты пользователя из руки."""
    player_cards = player.get_cover_cards()
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


def get_all_hand_cards(
    player: Player,
) -> Iterator[InlineQueryResultCachedSticker]:
    """Получает все карты пользователя, без действия при нажатии."""
    for i, cover_card in enumerate(player.hand):
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


def get_hand_query(player: Player) -> list[InlineQueryResultCachedSticker]:
    """Возвращает основную игровую клавиатуру."""
    # Если игрок сейчас не играет, то и действий никаких у него нету
    result = []
    if not player.is_current and not player.game.rules.intervention:
        return get_all_hand_cards(player)

    elif player.game.state == GameState.CHOOSE_COLOR:
        return get_color_query(player)

    elif player.game.state == GameState.TWIST_HAND:
        return select_player_query(player)

    elif player.game.take_flag:
        result = [
            _add_sticker("pass", stickers.OPTIONS.next_turn, "🃏 Пропускаю.")
        ]
    elif player.is_current:
        result = [
            _add_sticker(
                "take", stickers.OPTIONS.draw, take_cards_message(player.game)
            )
        ]

    if (
        isinstance(player.game.deck.top, TakeFourCard)
        and player.game.take_counter
    ):
        result.append(
            _add_sticker(
                "bluff",
                stickers.OPTIONS.bluff,
                "🍷 Ты блефуешь, показывай карты!",
            )
        )

    # Карты из руки уже отсортированы, остаётся только их добавить
    result.extend(get_hand_cards(player))

    # Явное отображение статуса игры
    result.append(
        _add_sticker(
            "status",
            stickers.OPTIONS.info,
            get_room_status(player.game),
        )
    )

    return result


# Настройки игровой комнаты
# =========================


def create_button(rule: str, status: bool) -> InlineKeyboardButton:
    """Создает кнопку для заданного правила."""
    status_sim = "🌟" if status else ""
    return InlineKeyboardButton(
        text=f"{status_sim}{rule.name}",
        callback_data=f"set:{rule.key}:{not status}",
    )


# TODO: Когда наконец игровые правила станут просто списком
def generate_buttons(game_rules: GameRules) -> InlineKeyboardMarkup:
    """Генерирует кнопки на основе правил игры."""
    buttons = [
        [create_button(rule, getattr(game_rules, rule.key, False))]
        for rule in RULES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
