"""Главный файл бота.

Здесь определены функции для запуска бота и регистрации всех обработчиков.
"""

import sys
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import (
    CallbackQuery,
    ChosenInlineResult,
    ErrorEvent,
    InlineQuery,
    Message,
    Update,
)
from aiogram.utils.token import TokenValidationError
from loguru import logger

from maubot.config import config, default, sm
from maubot.context import get_context
from maubot.events.journal import MessageJournal
from maubot.events.router import er
from maubot.handlers import ROUTERS

# Константы
# =========

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


@dp.message.middleware()  # type: ignore
@dp.inline_query.middleware()  # type: ignore
@dp.callback_query.middleware()  # type: ignore
@dp.chat_member.middleware()  # type: ignore
@dp.chosen_inline_result.middleware()  # type: ignore
async def game_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any],
) -> Callable[[Update, dict[str, Any]], Awaitable[Any]]:
    """Предоставляет экземпляр игры в обработчики сообщений."""
    if isinstance(
        event, CallbackQuery | ChosenInlineResult | InlineQuery | Message
    ):
        context = get_context(sm, event)
        data["game"] = context.game
        data["player"] = context.player
        data["channel"] = (
            sm._event_handler.get_channel(context.game.room_id)
            if context.game is not None
            else None
        )

    return await handler(event, data)


@dp.errors()
async def catch_errors(event: ErrorEvent) -> None:
    """Простой обработчик для ошибок."""
    logger.warning(event)
    logger.exception(event.exception)

    if event.update.callback_query:
        message = event.update.callback_query.message
    elif event.update.message:
        message = event.update.message
    else:
        message = None

    if message is None:
        logger.warning("No Message to send exception")
        return

    await message.answer(
        f"👀 <b>Что-то пошло не по плану</b>...\n{event.exception}"
    )


# Главная функция запуска бота
# ============================


async def main() -> None:
    """Запускает бота.

    Настраивает журнал действий.
    Загружает все необходимые обработчики.
    После запускает обработку событий бота.
    """
    logger.remove()
    logger.add(sys.stdout, format=LOG_FORMAT)

    logger.info("Setup bot ...")
    try:
        bot = Bot(config.telegram_token.get_secret_value(), default=default)
    except TokenValidationError as e:
        logger.error(e)
        sys.exit("Check your bot token in .env file.")

    logger.info("Load handlers ...")
    for router in ROUTERS:
        dp.include_router(router)
        logger.debug("Include router {}", router.name)

    logger.info("Set event handler")
    sm.set_handler(MessageJournal(bot, er))

    logger.success("Start polling!")
    await dp.start_polling(bot)
