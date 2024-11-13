"""Обрабатывает действия игрока во время хода.

Это касается обработки Inline query и при помощи него результатов.
"""

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineQuery
from loguru import logger

from maubot import keyboards

from maubot import keyboards, stickers
from maubot.config import config
from maubot.messages import HELP_MESSAGE
from maubot.uno.game import UnoGame
from maubot.uno.session import SessionManager

router = Router(name="Turn")

# Обработчики
# ===========

@router.message(Command("debug"))
async def debug_inline_queries(message: Message):
    """Отлаживает кнопочку выбора карты."""
    await message.answer("Тыкни сюда", reply_markup=keyboards.TURN_MARKUP)

@router.inline_query()
async def inline_handler(query: InlineQuery, game: UnoGame | None):
    """Обработчик inline запросов к бот."""
    logger.warning(game)

    if game is None:
        result = keyboards.NO_GAME_QUERY
    elif not game.started:
        result = keyboards.SELECT_GAME_QUERY
    else:
        result = keyboards.get_hand_query(game.get_player(query.from_user.id))
    
    await query.answer(result)
