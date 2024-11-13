"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение, пропуск хода.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from maubot import keyboards
from maubot.messages import NO_ROOM_MESSAGE, NOT_ENOUGH_PLAYERS
from maubot.uno.exceptions import (
    AlreadyJoinedError,
    DeckEmptyError,
    LobbyClosedError,
    NoGameInChatError,
    NotEnoughPlayersError,
)
from maubot.uno.game import UnoGame
from maubot.uno.session import SessionManager

router = Router(name="Player")

# Обработчики
# ===========

@router.message(Command("join"))
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
        await message.answer("🍰 Вы уже и без того с нами в комнате.")
    except DeckEmptyError:
        await message.answer("👀 К сожалению у нас не осталось для вас карт.")
    else:
        await message.answer((
            "🍰 Добро пожаловать к нам!\n"
            "Игра начнётся как все буудт в сборе."
        ))

@router.message(Command("leave"))
async def leave_player(message: Message,
    sm: SessionManager,
    game: UnoGame | None
):
    """Выход пользователя из игры."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    try:
        game.remove_player(message.from_user.id)
    except NoGameInChatError:
        return await message.answer("👀 Вас нет в комнате чтобы выйти из неё.")

    if game.started:
        status_message = (
            "🍰 Ладненько, следующих ход за "
            f"{game.player.user.mention_html()}."
        )
        markup = keyboards.TURN_MARKUP
    else:
        status_message = NOT_ENOUGH_PLAYERS
        markup = None
        sm.remove(message.chat.id)

    await message.answer(status_message, reply_markup=markup)