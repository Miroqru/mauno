"""Простые вспомогательные команды для бота."""

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from maubot.messages import HELP_MESSAGE

router = Router(name="simple commands")

STATUS_MESSAGE = (
    "🌟 <b>Немного о Mauno v2.0</b>:\n\n"
    "🃏 Это Telegram бот для игры с друзьями в групповом чате.\n"
    "Поддерживается Uno с множеством игровых правил для большего веселья.\n"
    "Исходный код проекта доступен в:\n"
    "- <a href='https://git.miroq.ru/salormoon/mauno'>Miroq</a>\n"
    "- <a href='https://github.com/miroqru/mauno'>Github</a>.\n"
    "🌱 Мы будем очень рады ваше <b>поддержке</b> в развитие бота.\n\n"
    "🪄 Следить за новостями можно в канале "
    "<a href='https://t.me/mili_qlaster'>Salorhard</a>."
)


@router.message(Command("help"))
async def get_help(message: Message, bot: Bot) -> None:
    """Помогает пользователю начать работать с ботом."""
    if message.chat.type == "private":
        await message.answer(HELP_MESSAGE)
        return None

    try:
        await message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )

    try:
        if message.from_user is not None:
            await bot.send_message(message.from_user.id, HELP_MESSAGE)
            await message.answer("✨ Помощь отправлена в личные сообщения.")
    except Exception as e:
        logger.warning("Unable to send private message: {}", e)
        await message.answer("👀 Я не могу написать вам первым.")


@router.message(Command("status"))
async def get_bot_status(message: Message) -> None:
    """Полезная информация о боте."""
    await message.answer(STATUS_MESSAGE)
