"""Редактор игровых правил."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from mau.game.game import MauGame
from mau.game.rules import GameRules
from maubot.filters import GameOwner

router = Router(name="Game rules")

ROOM_SETTINGS = (
    "⚙️ <b>Настройки комнаты</b>:\n\n"
    "В этом разделе вы можете настроить дополнительные параметры для игры.\n"
    "Они привносят дополнительное разнообразие в игровые правила.\n\n"
    "Пункты помеченные 🌟 <b>активированы</b> и уже наводят суету."
)


def rules_markup(game_rules: GameRules) -> InlineKeyboardMarkup:
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


@router.message(Command("rules"), GameOwner())
async def send_rules_list(message: Message, game: MauGame) -> None:
    """Отображает настройки для текущей комнаты."""
    await message.answer(ROOM_SETTINGS, reply_markup=rules_markup(game.rules))


@router.callback_query(F.data == "room_rules", GameOwner())
async def get_rules_call(query: CallbackQuery, game: MauGame) -> None:
    """Отображает настройки для текущей комнаты."""
    if isinstance(query.message, Message):
        await query.message.answer(
            ROOM_SETTINGS, reply_markup=rules_markup(game.rules)
        )
    await query.answer()


class RulesCallback(CallbackData, prefix="rule"):
    """Переключатель настроек."""

    index: int


@router.callback_query(RulesCallback.filter(), GameOwner())
async def edit_room_rules_call(
    query: CallbackQuery, callback_data: RulesCallback, game: MauGame
) -> None:
    """Изменяет настройки для текущей комнаты."""
    game.rules.toggle(callback_data.index)
    if isinstance(query.message, Message):
        await query.message.edit_text(
            ROOM_SETTINGS, reply_markup=rules_markup(game.rules)
        )
    await query.answer()
