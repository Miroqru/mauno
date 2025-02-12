"""Отображает информацию о пользователе."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberOwner,
    Message,
)

from maubot.db import User

router = Router(name="user")

# Обработчики
# ===========


@router.message(Command("user"))
async def user_info(message: Message) -> None:
    """Общая информация о пользователе."""
    if message.reply_to_message is not None:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    member = await message.chat.get_member(user.id)
    us, _ = await User.get_or_create(id=user.id)

    if isinstance(member, ChatMemberOwner | ChatMemberAdministrator):
        chat_status = f"{member.status}: {member.custom_title}"
    else:
        chat_status = ""

    if us.total_games == 0:
        win_pr = 0
    else:
        win_pr = round((us.first_places / us.total_games) * 100, 2)

    res = (
        f"[{message.chat.id} : {message.chat.type}]\n {message.chat.title}\n\n"
        f"<b>Пользователь</b> {user.mention_html()}:\n"
        f"[{user.id}] {user.full_name}\n{chat_status}\n\n"
        f"<b>Игр сыграно</b>: {us.total_games}\n"
        f"<b>Первых мест</b>: {us.first_places} ({win_pr}%)\n"
        f"<b>Карт разыграно</b>: {us.cards_played}\n"
    )

    await message.answer(res)
