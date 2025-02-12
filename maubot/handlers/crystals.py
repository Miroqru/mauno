"""Кристаллы.

Это внутри игровая валюта бота, используемая как плата для игровых
сессий.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
)

from maubot.db import User

router = Router(name="Crystals")

# Обработчики
# ===========


@router.message(Command("dayreward"))
async def user_info(message: Message) -> None:
    """Получает награду за ежедневный вход."""
    user = message.from_user
    us, _ = await User.get_or_create(id=user.id)
