"""Главный файл бота.

Здесь определены функции для запуска бота и регистрации всех обработчиков.
"""

import sys

from typing import Any, Callable, Awaitable

from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.types import Message, InlineQuery
from loguru import logger
from tortoise import Tortoise

from maubot.config import config, default
from maubot.handlers import ROUTERS
from maubot.uno.session import SessionManager

# Константы
# =========

sm = SessionManager()

dp = Dispatcher(
    # Добавляем менеджер игровых сессия в бота
    sm=sm
)

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
async def game_middleware(
    handler: Callable[[Message | InlineQuery, dict[str, Any]], Awaitable[Any]],
    event: Message | InlineQuery,
    data: dict[str, Any]
):
    """Предоставляет экземпляр игры в обработчики сообщений."""
    if isinstance(event, Message):
        game =  sm.games.get(event.chat.id)
        data["game"] = game
    elif isinstance(event, InlineQuery):
        chat_id = sm.user_to_chat.get(event.from_user.id)
        if chat_id is None:
            game = None
        else:
            game = sm.games.get(chat_id)
        data["game"] = game
        logger.debug("chat_id {} / game {} event {} {}", chat_id, game, type(event), event)

    if game is not None:
        data["player"] = game.get_player(event.from_user.id)
    else:
        data["player"] = None


    return await handler(event, data)


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
    logger.debug("Token: {}", config.db_url)

    logger.info("Setup bot ...")
    try:
        bot = Bot(
            token=config.token.get_secret_value(),
            default=default
        )
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
