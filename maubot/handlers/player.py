"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение, пропуск хода.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from maubot.uno.exceptions import (
    AlreadyJoinedError,
    DeckEmptyError,
    LobbyClosedError,
    NoGameInChatError,
)
from maubot.uno.game import UnoGame
from maubot.uno.session import SessionManager

router = Router(name="Player")

# Обработчики
# ===========


@router.message(Command('join'))
async def join_player(message: Message,
    sm: SessionManager,
    game: UnoGame | None
):
    """Подключает пользователя к игру."""
    try:
        sm.join(message.chat.id, message.from_user)
    except NoGameInChatError:
        await message.answer((
            "👀 В данном чате <b>нет игровой комнаты</b>.\n"
            "Создайте новую при помощи команды /game."
        ))
    except LobbyClosedError:
        await message.answer((
            "👀 К сожалению данная комната <b>закрыта</b>.\n"
            f"Вы можете попросить {game.start_player.mention_html()} открыть"
            "комнату."
        ))
    except AlreadyJoinedError:
        await message.answer("👀 Вы уже и без того с нами в комнате.")
    except DeckEmptyError:
        await message.answer("👀 К сожалению у нас не осталось для вас карт.")
    else:
        await message.answer((
            "🍰 Добро пожаловать к нам!\n"
            "Игра начнётся как все буудт в сборе."
        ))
