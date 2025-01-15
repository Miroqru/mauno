"""Главный файл бота.

Здесь определены функции для запуска бота и регистрации всех обработчиков.
"""

import sys
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    ErrorEvent,
    InlineQuery,
    Message,
    Update,
)
from aiogram.utils.token import TokenValidationError
from loguru import logger
from tortoise import Tortoise

from maubot.config import config, default
from maubot.handlers import ROUTERS
from maubot.uno.session import SessionManager

# Константы
# =========

sm = SessionManager()
dp = Dispatcher(sm=sm)


# Настраиваем формат отображения логов loguru
# Обратите внимание что в проекте помимо loguru используется logging
LOG_FORMAT = (
    "<light-black>{time:YYYY MM.DD HH:mm:ss.SSS}</> "
    "{file}:{function} "
    "<lvl>{message}</>"
)

# Middleware
# ==========

@dp.message.middleware()
@dp.inline_query.middleware()
@dp.callback_query.middleware()
@dp.chat_member.middleware()
@dp.chosen_inline_result.middleware()
async def game_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any]
):
    """Предоставляет экземпляр игры в обработчики сообщений."""
    if isinstance(event, (Message, ChatMemberUpdated)):
        game = sm.games.get(event.chat.id)
    elif isinstance(event, CallbackQuery):
        if event.message is None:
            chat_id = sm.user_to_chat.get(event.from_user.id)
            game = None if chat_id is None else sm.games.get(chat_id)
        else:
            game = sm.games.get(event.message.chat.id)
    elif isinstance(event, (InlineQuery, ChosenInlineResult)):
        chat_id = sm.user_to_chat.get(event.from_user.id)
        game = None if chat_id is None else sm.games.get(chat_id)

    data["game"] = game
    data["player"] = None if game is None else game.get_player(
        event.from_user.id
    )
    return await handler(event, data)

@dp.errors()
async def catch_errors(event: ErrorEvent):
    """Простой обработчик для ошибок."""
    logger.warning(event)
    logger.exception(event.exception)
    # await event.update.message.answer("Что-то явно пошло не по плану.")


# Главная функция запуска бота
# ============================

async def main():
    """Запускает бота.

    Настраивает логгирование.
    Загружает все необходимые обработчики.
    После запускает лонг поллинг.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        format=LOG_FORMAT
    )

    logger.info("Check config")
    logger.debug("Token: {}", config.token)
    logger.debug("DB url: {}", config.db_url)

    logger.info("Setup bot ...")
    try:
        bot = Bot(
            token=config.token.get_secret_value(),
            default=default
        )
        sm.bot = bot
    except TokenValidationError as e:
        logger.error(e)
        logger.info("Check your bot token in .env file.")
        sys.exit(1)

    logger.info("Load handlers ...")
    for router in ROUTERS:
        dp.include_router(router)
        logger.debug("Include router {}", router.name)

    logger.info("Init db connection ...")
    await Tortoise.init(
        db_url=config.db_url,
        modules={"models": ["maubot.db"]}
    )
    await Tortoise.generate_schemas()

    logger.success("Start polling!")
    await dp.start_polling(bot)
