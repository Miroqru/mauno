"""Управляет игровыми сессиями.

Позволяет создавать комнаты, удалять их, переключать настройки.
Если вас интересует взаимодействий игроков в сессиями, то перейдите
в роутер `player`.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from maubot.messages import NO_ROOM_MESSAGE, NOT_ENOUGH_PLAYERS
from maubot import keyboards, stickers
from maubot.config import config
from maubot.messages import HELP_MESSAGE
from maubot.uno.exceptions import NoGameInChatError
from maubot.uno.game import UnoGame
from maubot.uno.session import SessionManager

router = Router(name="Sessions")


# Обработчики
# ===========

@router.message(Command("game"))
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
        f"Автор: {game.start_player.mention_html()}\n\n{members_list}\n"
        "- /join чтобы присоединиться к игре\n"
        "- /start для начала веселья"
    ))

@router.message(Command("start"))
async def start_gama(message: Message, game: UnoGame | None):
    """Запускает игру в комнате."""
    if message.chat.type == "private":
        return await message.answer(HELP_MESSAGE)

    if game is None:
        await message.answer(NO_ROOM_MESSAGE)

    elif game.started:
        await message.answer("👀 Игра уже началась.")

    elif len(game.players) < config.min_players:
        await message.answer9(NOT_ENOUGH_PLAYERS)

    else:
        game.start()
        await message.answer_sticker(
            stickers.NORMAL[stickers.to_str(game.deck.top)]
        )

        await message.answer((
                "🍰 Да начнётся <b>Новая игра!</b>!\n"
                f"И первым у нас ходит {game.player.user.mention_html()}\n"
                "/close чтобы закрыть комнату от посторонних."
            ),
            reply_markup=keyboards.TURN_MARKUP
        )

@router.message(Command("stop"))
async def stop_gama(message: Message, game: UnoGame | None, sm: SessionManager):
    """Принудительно завершает текущую игру."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    player = game.get_player(message.from_user.id)
    if player is None or player.user.id != game.start_player.id:
        return await message.answer(
            "👀 Только создатель комнаты может завершить игру."
        )

    sm.remove(game.chat_id)
    await message.answer("🧹 Игра была добровольно-принудительно завершена.")


# Управление настройками комнаты
# ==============================

@router.message(Command("open"))
async def open_gama(message: Message, game: UnoGame | None, sm: SessionManager):
    """Открывает игровую комнату для всех участников чата."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    player = game.get_player(message.from_user.id)
    if player is None or player.user.id != game.start_player.id:
        return await message.answer(
            "👀 Только создатель комнаты может открыть комнату."
        )

    game.open = True
    await message.answer(
        "🧹 Комната <b>открыта</b>!\n любой участник может зайти (/join)."
    )

@router.message(Command("close"))
async def close_gama(message: Message,
    game: UnoGame | None,
    sm: SessionManager
):
    """Закрывает игровую комнату для всех участников чата."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    player = game.get_player(message.from_user.id)
    if player is None or player.user.id != game.start_player.id:
        return await message.answer(
            "👀 Только создатель комнаты может закрыть комнату."
        )

    game.open = False
    await message.answer(
        "🧹 Комната <b>закрыта</b>.\nНикто не помешает вам доиграть."
    )


# Управление участниками комнатами
# ================================

@router.message(Command("kick"))
async def kick_player(message: Message,
    game: UnoGame | None,
    sm: SessionManager
):
    """Выкидывает участника из комнаты."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    if not game.started:
        return await message.answer(
            "🍰 Игра ещё не началась, пока рано выкидывать участников."
        )

    player = game.get_player(message.from_user.id)
    if player is None or player.user.id != game.start_player.id:
        return await message.answer(
            "👀 Только создатель комнаты может закрыть комнату."
        )

    if message.reply_to_message is None:
        return await message.answer(
            "👀 Перешлите сообщение негодника, которого нужно исключить."
        )

    kicked_user = message.reply_to_message.from_user
    try:
        game.remove_player(kicked_user.id)
    except NoGameInChatError:
        return message.answer(
            "👀 Указанный пользователь даже не играет с нами."
        )

    status_message = (
        f"🧹 {game.start_player.mention_html()} выгнал "
        f"{kicked_user.mention_html()} из игры за плохое поведение.\n"
    )
    if game.started:
        status_message += (
            "🍰 Ладненько, следующих ход за "
            f"{game.player.user.mention_html()}."
        )
        markup = keyboards.TURN_MARKUP
    else:
        sm.remove(message.chat.id)
        status_message += NOT_ENOUGH_PLAYERS
        markup = None

    await message.answer(status_message, reply_markup=markup)
