"""Редактор колоды.

Позволяет редактировать игровую колоду до начала игры.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from mau.deck import DeckParams
from mau.game import UnoGame
from maubot import filters

router = Router(name="Deck editor")


# Вспомогательные методы
# ======================


def _color_status(params: DeckParams) -> str:
    return "".join([str(c) for c in params.colors])


def _groups_status(params: DeckParams) -> str:
    res = ""
    for group in params.groups:
        res += f"\n-- {group.card_type}({group.value}) x{group.count}"
    return res


def _wild_status(params: DeckParams) -> str:
    res = ""
    for group in params.wild_groups:
        res += f"\n-- {group.card_type} x{group.count}"
    return res


def get_deck_status(params: DeckParams) -> str:
    """Получает информацию о клоде карт."""
    return (
        f"Цвета:{_color_status(params)}\n\n"
        f"Карты:{_groups_status(params)}\n\n"
        f"Дикие карты:{_wild_status(params)}"
    )


# Клавиатуры
# ==========

_EDITOR_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пресеты", callback_data="deck_preset")],
        [
            InlineKeyboardButton(text="Добавить", callback_data="deck_add"),
            InlineKeyboardButton(text="Удалить", callback_data="deck_remove"),
        ],
    ]
)

# Обработчики
# ===========


@router.message(Command("deck"), filters.ActivePlayer())
async def get_editor_message(message: Message, game: UnoGame) -> None:
    """Получает сообщение редактора колод."""
    await message.answer(
        get_deck_status(game.deck_params), reply_markup=_EDITOR_MARKUP
    )


@router.callback_query(F.data == "deck", filters.ActivePlayer())
async def deck_editor_call(query: CallbackQuery, game: UnoGame):
    await query.message.answer(
        get_deck_status(game.deck_params), reply_markup=_EDITOR_MARKUP
    )
    await query.answer()
