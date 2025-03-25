"""Управляет игровыми сессиями.

Позволяет создавать комнаты, удалять их, переключать настройки.
Если вас интересует взаимодействий игроков в сессиями, то перейдите
в роутер `player`.
"""

import random

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from loguru import logger

from mau.card import CardColor
from mau.exceptions import NoGameInChatError, NotEnoughPlayersError
from mau.game import UnoGame
from mau.player import BaseUser
from mau.session import SessionManager
from maubot import filters, keyboards
from maubot.config import config
from maubot.events.journal import MessageChannel
from maubot.messages import HELP_MESSAGE, NO_ROOM_MESSAGE

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
        if message.from_user is None:
            raise ValueError("None User tries create new game")

        game = sm.create(
            str(message.chat.id),
            BaseUser(
                str(message.from_user.id), message.from_user.mention_html()
            ),
        )

    if game.started:
        await message.answer(
            "🔑 Игра уже начата. Для начала её нужно завершить. (/stop)"
        )


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


@router.message(Command("stop"), filters.GameOwner())
async def stop_gama(
    message: Message, game: UnoGame, sm: SessionManager
) -> None:
    """Принудительно завершает текущую игру."""
    sm.remove(game.room_id)


# Управление настройками комнаты
# ==============================


@router.message(Command("open"), filters.GameOwner())
async def open_gama(message: Message, game: UnoGame) -> None:
    """Открывает игровую комнату для всех участников чата."""
    game.open = True
    await message.answer(
        "🍰 Комната <b>открыта</b>!\n любой участник может зайти (/join)."
    )


@router.message(Command("close"), filters.GameOwner())
async def close_gama(message: Message, game: UnoGame) -> None:
    """Закрывает игровую комнату для всех участников чата."""
    game.open = False
    await message.answer(
        "🔒 Комната <b>закрыта</b>.\nНикто не помешает вам доиграть."
    )


# Управление участниками комнатами
# ================================


@router.message(Command("kick"), filters.GameOwner())
async def kick_player(
    message: Message, game: UnoGame, sm: SessionManager, channel: MessageChannel
) -> None:
    """Выкидывает участника из комнаты."""
    if (
        message.reply_to_message is None
        or message.reply_to_message.from_user is None
    ):
        raise ValueError(
            "🍷 Перешлите сообщение негодника, которого нужно исключить."
        )

    kicked_user = message.reply_to_message.from_user
    kick_player = game.get_player(str(kicked_user.id))
    channel.add(
        f"🧹 {game.owner.name} выгнал "
        f"{kicked_user} из игры за плохое поведение.\n"
    )
    await channel.send()
    if kick_player is not None:
        sm.leave(kick_player)


@router.message(Command("skip"), filters.GameOwner())
async def skip_player(
    message: Message, game: UnoGame, channel: MessageChannel
) -> None:
    """пропускает участника за долгое бездействие."""
    game.take_counter += 1
    game.player.take_cards()
    skip_player = game.player
    channel.add(
        f"☕ {skip_player.name} потерял свои ку.. карты.\n"
        "Мы их нашли и дали игроку ещё немного карт от нас.\n"
    )
    # Иногда может быть такое, что пропускается чёрная карта
    # Тогда ей нужно дать какой-нибудь цвет
    if game.deck.top.color == CardColor.BLACK:
        game.choose_color(CardColor(random.randint(0, 3)))
    else:
        game.next_turn()
    await channel.send()


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


# Настройки комнаты
# =================


@router.message(Command("rules"), filters.ActivePlayer())
async def send_rules_list(message: Message, game: UnoGame) -> None:
    """Отображает настройки для текущей комнаты."""
    await message.answer(
        ROOM_SETTINGS, reply_markup=keyboards.get_rules_markup(game.rules)
    )


@router.callback_query(F.data == "room_rules", filters.ActivePlayer())
async def get_rules_call(query: CallbackQuery, game: UnoGame) -> None:
    """Отображает настройки для текущей комнаты."""
    if isinstance(query.message, Message):
        await query.message.answer(
            ROOM_SETTINGS,
            reply_markup=keyboards.get_rules_markup(game.rules),
        )
    await query.answer()


class RulesCallback(CallbackData, prefix="rule"):
    """Переключатель настроек."""

    key: str
    value: bool


@router.callback_query(RulesCallback.filter(), filters.ActivePlayer())
async def edit_room_rules_call(
    query: CallbackQuery, callback_data: RulesCallback, game: UnoGame
) -> None:
    """Изменяет настройки для текущей комнаты."""
    getattr(game.rules, callback_data.key).status = callback_data.value
    if isinstance(query.message, Message):
        await query.message.edit_text(
            ROOM_SETTINGS,
            reply_markup=keyboards.get_rules_markup(game.rules),
        )
    await query.answer()
