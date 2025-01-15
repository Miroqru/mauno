"""Управляет игровыми сессиями.

Позволяет создавать комнаты, удалять их, переключать настройки.
Если вас интересует взаимодействий игроков в сессиями, то перейдите
в роутер `player`.
"""

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from loguru import logger

from maubot import keyboards, messages, stickers
from maubot.config import config
from maubot.messages import HELP_MESSAGE, NO_ROOM_MESSAGE, NOT_ENOUGH_PLAYERS
from maubot.uno.exceptions import NoGameInChatError
from maubot.uno.game import UnoGame
from maubot.uno.session import SessionManager

router = Router(name="Sessions")

ROOM_SETTINGS = (
    "⚙️ <b>Настройки комнаты</b>:\n\n"
    "В этом разделе вы можете настроить дополнительные параметры для игры.\n"
    "Они привносят дополнительное разнообразие в игровые правила.\n\n"
    "Пункты помеченные 🌟 <b>активированы</b> и уже наводят суету."
)


# Обработчики
# ===========

@router.message(Command("game"))
async def create_game(message: Message,
    sm: SessionManager,
    game: UnoGame | None,
    bot: Bot
):
    """Создаёт новую комнату."""
    if message.chat.type == "private":
        return await message.answer("👀 Игры создаются в групповом чате.")

    # Если игра ещё не началась, получаем её
    if game is None:
        game = sm.create(message.chat.id)
        game.start_player = message.from_user
    elif game.started:
        game.journal.add(
            "🔑 Игра уже начата. Для начала её нужно завершить. (/stop)"
        )
        await game.journal.send_journal()

    lobby_message = await message.answer(
        messages.get_room_status(game),
        reply_markup=keyboards.get_room_markup(game)
    )
    # Добавляем ID сообщения с лобби, чтобы после редактировать его
    game.lobby_message = lobby_message.message_id

@router.message(Command("start"))
async def start_gama(message: Message, game: UnoGame | None):
    """Запускает игру в комнате."""
    if message.chat.type == "private":
        return await message.answer(HELP_MESSAGE)

    if game is None:
        await message.answer(NO_ROOM_MESSAGE)

    elif game.started:
        await message.answer("👀 Игра уже началась ранее.")

    elif len(game.players) < config.min_players:
        await message.answer9(NOT_ENOUGH_PLAYERS)

    else:
        try:
            await message.delete()
        except Exception as e:
            logger.warning("Unable to delete message: {}", e)
            await message.answer(
                "🧹 Пожалуйста выдайте мне права удалять сообщения в чате."
            )

        game.start()
        await message.answer_sticker(
            stickers.NORMAL[stickers.to_sticker_id(game.deck.top)]
        )

        game.journal.add(messages.get_new_game_message(game))
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()

@router.message(Command("stop"))
async def stop_gama(message: Message, game: UnoGame | None, sm: SessionManager):
    """Принудительно завершает текущую игру."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    player = game.get_player(message.from_user.id)
    if player is None or not player.is_owner:
        return await message.answer(
            "👀 Только создатель комнаты может завершить игру."
        )

    sm.remove(game.chat_id)
    await message.answer(
        "🧹 Игра была добровольно-принудительно остановлена.\n"
        f"{messages.end_game_message(game)}"
    )


# Управление настройками комнаты
# ==============================

@router.message(Command("open"))
async def open_gama(message: Message, game: UnoGame | None, sm: SessionManager):
    """Открывает игровую комнату для всех участников чата."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    player = game.get_player(message.from_user.id)
    if player is None or not player.is_owner:
        return await message.answer(
            "👀 Только создатель комнаты может открыть комнату."
        )

    game.open = True
    await message.answer(
        "🍰 Комната <b>открыта</b>!\n любой участник может зайти (/join)."
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
    if player is None or not player.is_owner:
        return await message.answer(
            "👀 Только создатель комнаты может закрыть комнату."
        )

    game.open = False
    await message.answer(
        "🔒 Комната <b>закрыта</b>.\nНикто не помешает вам доиграть."
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
    if player is None or not  player.is_owner:
        return await message.answer(
            "👀 Только создатель комнаты может выгнать участника."
        )

    if message.reply_to_message is None:
        return await message.answer(
            "🍷 Перешлите сообщение негодника, которого нужно исключить."
        )

    kicked_user = message.reply_to_message.from_user
    try:
        game.remove_player(kicked_user.id)
    except NoGameInChatError:
        return message.answer(
            "👀 Указанный пользователь даже не играет с нами."
        )

    game.journal.add(
        f"🧹 {game.start_player.mention_html()} выгнал "
        f"{kicked_user.mention_html()} из игры за плохое поведение.\n"
    )
    if game.started:
        game.journal.add(
            "🍰 Ладненько, следующих ход за "
            f"{game.player.user.mention_html()}."
        )
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        await message.answer(
            f"{NOT_ENOUGH_PLAYERS}\n\n{messages.end_game_message(game)}"
        )
        sm.remove(message.chat.id)

@router.message(Command("skip"))
async def skip_player(message: Message,
    game: UnoGame | None,
    sm: SessionManager
):
    """пропускает участника за долгое бездействие."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    if not game.started:
        return await message.answer(
            "🍰 Игра ещё не началась, пока рано выкидывать участников."
        )

    player = game.get_player(message.from_user.id)
    if player is None or not player.is_owner:
        return await message.answer(
            "👀 Только создатель комнаты может пропустить игрока."
        )

    game.take_counter += 1
    game.player.take_cards()
    skip_player = game.player
    game.next_turn()
    game.journal.add(
        f"☕ {skip_player.user.mention_html()} потерял свои ку.. карты.\n"
        "Мы их нашли и дали игроку ещё немного карт от нас.\n"
        "🍰 Ладненько, следующих ход за "
        f"{game.player.user.mention_html()}."
    )
    game.journal.set_markup(keyboards.TURN_MARKUP)
    await game.journal.send_journal()


# Обработчики событий
# ===================

@router.callback_query(F.data=="start_game")
async def start_game_call(query: CallbackQuery, game: UnoGame | None):
    """Запускает игру в комнате."""
    try:
        await query.message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await query.message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )

    game.start()
    await query.message.answer_sticker(
        stickers.NORMAL[stickers.to_sticker_id(game.deck.top)]
    )

    game.journal.add(messages.get_new_game_message(game))
    game.journal.set_markup(keyboards.TURN_MARKUP)
    await game.journal.send_journal()


# Настройки комнаты
# =================

@router.message(Command("settings"))
async def settings_menu(message: Message, game: UnoGame | None):
    """Отображает настройки для текущей комнаты."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    await message.answer(ROOM_SETTINGS,
        reply_markup=keyboards.get_settings_markup(game.rules)
    )

@router.callback_query(F.data=="room_settings")
async def settings_menu_call(query: CallbackQuery, game: UnoGame | None):
    """Отображает настройки для текущей комнаты."""
    if game is None:
        return await query.message.answer(NO_ROOM_MESSAGE)

    await query.message.answer(ROOM_SETTINGS,
        reply_markup=keyboards.get_settings_markup(game.rules)
    )
    await query.answer()

class SettingsCallback(CallbackData, prefix="set"):
    """Переключатель настроек."""

    key: str
    value: bool

@router.callback_query(SettingsCallback.filter())
async def edit_room_settings_call(query: CallbackQuery,
    callback_data: SettingsCallback,
    game: UnoGame | None
):
    """Изменяет настройки для текущей комнаты."""
    if game is None:
        return await query.message.answer(NO_ROOM_MESSAGE)

    setattr(game.rules, callback_data.key, callback_data.value)
    await query.message.edit_text(ROOM_SETTINGS,
        reply_markup=keyboards.get_settings_markup(game.rules)
    )
