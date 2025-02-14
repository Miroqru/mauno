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

from mau.exceptions import (
    GameNotStartedError,
    NoGameInChatError,
    NotEnoughPlayersError,
    NotGameOwnerError,
)
from mau.game import UnoGame
from mau.messages import end_game_message
from mau.session import SessionManager
from maubot import keyboards, messages
from maubot.config import config, stickers
from maubot.messages import HELP_MESSAGE, NO_ROOM_MESSAGE, NOT_ENOUGH_PLAYERS

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
async def create_game(
    message: Message, sm: SessionManager, game: UnoGame | None, bot: Bot
) -> None:
    """Создаёт новую комнату."""
    if message.chat.type == "private":
        await message.answer("👀 Игры создаются в групповом чате.")

    # Если игра ещё не началась, получаем её
    if game is None:
        game = sm.create(str(message.chat.id))
        # FIXME: И вновь game.owner
        game.start_player = message.from_user  # type: ignore
    elif game.started:
        game.journal.add(
            "🔑 Игра уже начата. Для начала её нужно завершить. (/stop)"
        )
        await game.journal.send_journal()

    lobby_message = await message.answer(
        messages.get_room_status(game),
        reply_markup=keyboards.get_room_markup(game),
    )
    # Добавляем ID сообщения с лобби, чтобы после редактировать его
    game.lobby_message = lobby_message.message_id


@router.message(Command("start"))
async def start_gama(message: Message, game: UnoGame | None) -> None:
    """Запускает игру в комнате."""
    if message.chat.type == "private":
        await message.answer(HELP_MESSAGE)
        return None

    if game is None:
        await message.answer(NO_ROOM_MESSAGE)

    elif game.started:
        await message.answer("👀 Игра уже началась ранее.")

    elif len(game.players) < config.min_players:
        raise NotEnoughPlayersError

    else:
        try:
            await message.delete()
        except Exception as e:
            logger.warning("Unable to delete message: {}", e)
            await message.answer(
                "🧹 Пожалуйста выдайте мне права удалять сообщения в чате."
            )

        game.start()
        await message.answer_sticker(stickers.normal[game.deck.top.to_str()])
        game.journal.add(messages.get_new_game_message(game))
        await game.journal.send_journal()


@router.message(Command("stop"))
async def stop_gama(
    message: Message, game: UnoGame | None, sm: SessionManager
) -> None:
    """Принудительно завершает текущую игру."""
    if game is None or message.from_user is None:
        raise NoGameInChatError

    player = game.get_player(str(message.from_user.id))
    if player is None or not player.is_owner:
        raise NotGameOwnerError

    sm.remove(game.room_id)
    await message.answer(
        "🧹 Игра была добровольно-принудительно остановлена.\n"
        f"{end_game_message(game)}"
    )


# Управление настройками комнаты
# ==============================


@router.message(Command("open"))
async def open_gama(
    message: Message, game: UnoGame | None, sm: SessionManager
) -> None:
    """Открывает игровую комнату для всех участников чата."""
    if game is None or message.from_user is None:
        raise NoGameInChatError

    player = game.get_player(str(message.from_user.id))
    if player is None or not player.is_owner:
        raise NotGameOwnerError

    game.open = True
    await message.answer(
        "🍰 Комната <b>открыта</b>!\n любой участник может зайти (/join)."
    )


@router.message(Command("close"))
async def close_gama(
    message: Message, game: UnoGame | None, sm: SessionManager
) -> None:
    """Закрывает игровую комнату для всех участников чата."""
    if game is None or message.from_user is None:
        raise NoGameInChatError

    player = game.get_player(str(message.from_user.id))
    if player is None or not player.is_owner:
        raise NotGameOwnerError

    game.open = False
    await message.answer(
        "🔒 Комната <b>закрыта</b>.\nНикто не помешает вам доиграть."
    )


# Управление участниками комнатами
# ================================


@router.message(Command("kick"))
async def kick_player(
    message: Message, game: UnoGame | None, sm: SessionManager
) -> None:
    """Выкидывает участника из комнаты."""
    if game is None or message.from_user is None:
        raise NoGameInChatError

    if not game.started:
        raise GameNotStartedError

    player = game.get_player(str(message.from_user.id))
    if player is None or not player.is_owner:
        raise NotGameOwnerError

    if (
        message.reply_to_message is None
        or message.reply_to_message.from_user is None
    ):
        raise NoGameInChatError(
            "🍷 Перешлите сообщение негодника, которого нужно исключить."
        )

    kicked_user = message.reply_to_message.from_user
    game.remove_player(str(kicked_user.id))

    game.journal.add(
        # TODO: game.owner тут должен быть
        f"🧹 {game.start_player.mention_html()} выгнал "  # type: ignore
        f"{kicked_user} из игры за плохое поведение.\n"
    )
    if game.started:
        game.journal.add(f"🍰 Ладненько, следующих ход за {game.player.name}.")
        await game.journal.send_journal()
    else:
        await message.answer(
            f"{NOT_ENOUGH_PLAYERS}\n\n{end_game_message(game)}"
        )
        sm.remove(message.chat.id)


@router.message(Command("skip"))
async def skip_player(
    message: Message, game: UnoGame | None, sm: SessionManager
) -> None:
    """пропускает участника за долгое бездействие."""
    # FIXME: Чутка костыльно получилось
    if game is None or message.from_user is None:
        raise NoGameInChatError

    if not game.started:
        raise GameNotStartedError

    player = game.get_player(str(message.from_user.id))
    if player is None or not player.is_owner:
        raise NotGameOwnerError

    game.take_counter += 1
    game.player.take_cards()
    skip_player = game.player
    game.next_turn()
    game.journal.add(
        f"☕ {skip_player.name} потерял свои ку.. карты.\n"
        "Мы их нашли и дали игроку ещё немного карт от нас.\n"
        "🍰 Ладненько, следующих ход за "
        f"{game.player.name}."
    )
    await game.journal.send_journal()


# Обработчики событий
# ===================


@router.callback_query(F.data == "start_game")
async def start_game_call(query: CallbackQuery, game: UnoGame | None) -> None:
    """Запускает игру в комнате."""
    if not isinstance(query.message, Message):
        raise ValueError("Query.message is not a Message")

    try:
        await query.message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await query.message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )

    if game is None:
        raise NoGameInChatError

    game.start()
    await query.message.answer_sticker(stickers.normal[game.deck.top.to_str()])

    game.journal.add(messages.get_new_game_message(game))
    await game.journal.send_journal()


# Настройки комнаты
# =================


@router.message(Command("settings"))
async def settings_menu(message: Message, game: UnoGame | None) -> None:
    """Отображает настройки для текущей комнаты."""
    if game is None:
        raise NoGameInChatError

    await message.answer(
        ROOM_SETTINGS, reply_markup=keyboards.get_settings_markup(game.rules)
    )


@router.callback_query(F.data == "room_settings")
async def settings_menu_call(
    query: CallbackQuery, game: UnoGame | None
) -> None:
    """Отображает настройки для текущей комнаты."""
    if game is None:
        raise NoGameInChatError

    if isinstance(query.message, Message):
        await query.message.edit_text(
            ROOM_SETTINGS,
            reply_markup=keyboards.get_settings_markup(game.rules),
        )
    await query.answer()


class SettingsCallback(CallbackData, prefix="set"):
    """Переключатель настроек."""

    key: str
    value: bool


@router.callback_query(SettingsCallback.filter())
async def edit_room_settings_call(
    query: CallbackQuery, callback_data: SettingsCallback, game: UnoGame | None
) -> None:
    """Изменяет настройки для текущей комнаты."""
    if game is None:
        raise NoGameInChatError

    getattr(game.rules, callback_data.key).status = callback_data.value
    if isinstance(query.message, Message):
        await query.message.edit_text(
            ROOM_SETTINGS,
            reply_markup=keyboards.get_settings_markup(game.rules),
        )
    await query.answer()
