"""Управляет игровыми сессиями.

Позволяет создавать комнаты, удалять их, переключать настройки.
Если вас интересует взаимодействий игроков в сессиями, то перейдите
в роутер `player`.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from maubot.config import config
from maubot.messages import HELP_MESSAGE
from maubot.uno.game import UnoGame
from maubot.uno.session import SessionManager

router = Router(name="Sessions")

# Обработчики
# ===========

@router.message(Command('game'))
async def create_game(message: Message,
    sm: SessionManager,
    game: UnoGame | None
):
    """Создаёт новую комнату."""
    if message.chat.type == "private":
        return await message.answer("👀 Игры создаются в групповом чате.")

    # Если игра ещё не началась, получаем её
    if game is None or game.started:
        game = sm.create(message.chat.id)
        game.start_player = message.from_user
        create_status = "☕ <b>Создано новая комната</b> для игры."
    else:
        create_status = "☕ <b>Текущая комната</b> для игры."

    members_list = f"✨ Участники ({len(game.players)}):\n"
    for player in game.players:
        members_list += f"- {player.user.mention_html()}\n"

    await message.answer((
        f"{create_status}\n"
        f"Автор: {game.start_player.mention_html()}\n\n{members_list}\n\n"
        "- /join чтобы присоединиться к игре\n"
        "- /start для начала веселья"
    ))

@router.message(Command("start"))
async def start_gama(message: Message,
    sm: SessionManager,
    game: UnoGame | None
):
    """Запускает игру в комнате."""
    if message.chat.type == "private":
        return await message.answer(HELP_MESSAGE)

    if game is None:
        await message.answer((
            "👀 В данном чате <b>нет игровой комнаты</b>.\n"
            "Создайте новую при помощи команды /game."
        ))

    elif game.started:
        await message.answer("👀 Игра уже началась.")

    elif len(game.players) < config.min_players:
        await message.answer9((
            f"👀 <b>Недостаточно игроков<b> (минимум {config.min_players}) для "
            "начала игры.\n"
            "Воспользуйтесь командой /join чтобы присоединиться к игре."
        ))

    else:
        game.start()

        # TODO: Отправка первого сообщения