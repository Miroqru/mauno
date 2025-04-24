"""Простые вспомогательные команды для бота."""

from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from mau.deck_generator import (
    CARD_PRESETS,
    CardGroup,
    DeckGenerator,
    DeckPreset,
)
from mau.game import UnoGame
from maubot.filters import GameOwner

router = Router(name="Deck editor")

# Сообщений
# =========


def get_presets(presets: dict[str, DeckPreset]) -> InlineKeyboardMarkup:
    """Собирает клавиатуру доступных шаблонов колоды."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=preset.name, callback_data=f"preset:{name}"
                )
            ]
            for name, preset in presets.items()
        ]
    )


def get_deck_info(groups: list[CardGroup]) -> str:
    """Собирает сообщение с выбранными правилами генератора колоды."""
    res = ""
    for group in groups:
        colors = "".join(str(color) for color in group.colors)
        res += (
            f"\n{colors} <code>{group.card_type.name}</code> "
            f"{group.value} / x{group.count}"
        )
    return res


def deck_editor_message(groups: list[CardGroup]) -> str:
    """Собирает сообщение редактора колоды."""
    return (
        "✏️ <b>Редактор колоды</b>:\n"
        f"{get_deck_info(groups)}\n\n"
        "💡 Вы можете выбрать один из готовых <b>шаблонов</b>."
    )


# Обработчики
# ===========


@router.callback_query(F.data == "deck_edit", GameOwner())
async def get_deck_editor(query: CallbackQuery, game: UnoGame) -> None:
    """Получает сообщение редактора колоды с готовыми шаблонами."""
    await query.answer()
    await query.message.answer(
        deck_editor_message(game.deck_generator.groups),
        reply_markup=get_presets(CARD_PRESETS),
    )


class PresetCallback(CallbackData, prefix="preset"):
    """Клавиатура выбора шаблона колоды."""

    name: str


@router.callback_query(PresetCallback.filter())
async def set_deck_preset(
    query: CallbackQuery, game: UnoGame, callback_data: PresetCallback
) -> None:
    """Выбирает один из заготовленных шаблонов колоды для игры."""
    await query.answer()
    game.deck_generator = DeckGenerator.from_preset(callback_data.name)
    await query.message.edit_text(
        deck_editor_message(game.deck_generator.groups),
        reply_markup=get_presets(CARD_PRESETS),
    )
