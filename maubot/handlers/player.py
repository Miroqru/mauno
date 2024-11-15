"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение, пропуск хода.
"""

from aiogram import Bot, F, Router
from aiogram.filters import (
    IS_MEMBER,
    IS_NOT_MEMBER,
    ChatMemberUpdatedFilter,
    Command,
)
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message
from loguru import logger

from maubot import keyboards
from maubot.messages import (
    NO_ROOM_MESSAGE,
    NOT_ENOUGH_PLAYERS,
    get_room_status,
)
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

@router.message(Command("join"))
async def join_player(message: Message,
    sm: SessionManager,
    game: UnoGame | None,
    bot: Bot
):
    """Подключает пользователя к игре."""
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
        try:
            await message.delete()
        except Exception as e:
            logger.warning("Unable to delete message: {}", e)
            await message.answer(
                "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
            )

    if game is not None and not game.started:
        await bot.edit_message_text(
            text=get_room_status(game),
            chat_id=game.chat_id,
            message_id=game.lobby_message,
            reply_markup=keyboards.get_room_markup(game)
        )

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
        sm.user_to_chat.pop(message.from_user.id)
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


# Обработчики для кнопок
# ======================

@router.callback_query(F.data=="join")
async def join_callback(query: CallbackQuery,
    sm: SessionManager,
    game: UnoGame |  None
):
    """Добавляет игрока в текущую комнату."""
    try:
        sm.join(query.message.chat.id, query.from_user)
    except LobbyClosedError:
        await query.message.answer((
            "👀 К сожалению данная комната <b>закрыта</b>.\n"
            f"Вы можете попросить {game.start_player.mention_html()} открыть"
            "комнату."
        ))
    except AlreadyJoinedError:
        await query.message.answer("🍰 Вы уже и без того с нами в комнате.")
    except DeckEmptyError:
        await query.message.answer(
            "👀 К сожалению у нас не осталось для вас карт."
        )
    else:
        await query.message.edit_text(
            text=get_room_status(game),
            reply_markup=keyboards.get_room_markup(game)
        )


# Обработчики событий
# ===================

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated,
    game: UnoGame | None,
    sm: SessionManager
):
    """Исключаем пользователя, если тот осмелился выйти из чата."""
    if game is None:
        return

    try:
        game.remove_player(event.from_user.id)
        sm.user_to_chat.pop(event.from_user.id)
    except NoGameInChatError:
        pass

    if game.started:
        status_message = (
           f"🍰 Ладненько, следующих ход за {game.player.user.mention_html()}."
        )
        markup = keyboards.TURN_MARKUP
    else:
        status_message = NOT_ENOUGH_PLAYERS
        markup = None
        sm.remove(event.chat.id)

    await event.answer(status_message, reply_markup=markup)
