"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger

from mau.card import TakeCard, TakeFourCard
from mau.enums import GameState
from mau.exceptions import AlreadyJoinedError
from mau.game import UnoGame
from mau.player import BaseUser, Player
from mau.session import SessionManager
from maubot import filters
from maubot.events.journal import MessageChannel

router = Router(name="Player")

# Обработчики
# ===========


@router.message(Command("join"), filters.ActiveGame())
async def join_player(message: Message, sm: SessionManager) -> None:
    """Подключает пользователя к игре."""
    if message.from_user is None:
        raise ValueError("User can`t be none")

    sm.join(
        str(message.chat.id),
        BaseUser(str(message.from_user.id), message.from_user.mention_html()),
    )

    try:
        await message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )


@router.message(Command("leave"), filters.ActivePlayer())
async def leave_player(
    message: Message, sm: SessionManager, player: Player
) -> None:
    """Выход пользователя из игры."""
    sm.leave(player)


# Обработчики для кнопок
# ======================


@router.callback_query(F.data == "join", filters.ActiveGame())
async def join_callback(query: CallbackQuery, sm: SessionManager) -> None:
    """Добавляет игрока в текущую комнату."""
    if not isinstance(query.message, Message):
        raise ValueError("Query message should be Message instance")

    try:
        sm.join(
            str(query.message.chat.id),
            BaseUser(str(query.from_user.id), query.from_user.mention_html()),
        )
    except AlreadyJoinedError:
        await query.answer("👋 Вы уже с нами в комнате")


@router.callback_query(F.data == "take", filters.NowPlaying())
async def take_cards_call(
    query: CallbackQuery, game: UnoGame, player: Player, channel: MessageChannel
) -> None:
    """Игрок выбирает взять карты."""
    if game.player == player:
        channel.add("🃏 Вы решили что будет проще <b>взять карты</b>.")
    else:
        game.set_current_player(player)
        channel.add(f"🃏 {player.name} решил <b>взять карты</b>.")

    player.take_cards()

    # Если пользователь сам взял карты, то не нужно пропускать ход
    if isinstance(game.deck.top, TakeCard | TakeFourCard) and game.take_counter:
        game.next_turn()
    else:
        channel.add(f"☕ {game.player.name} <b>продолжает</b>.")
        await channel.send()


@router.callback_query(F.data == "shot", filters.NowPlaying())
async def shotgun_call(
    query: CallbackQuery,
    sm: SessionManager,
    game: UnoGame,
    player: Player,
    channel: MessageChannel,
) -> None:
    """Игрок выбирает взять карты."""
    res = player.shotgun()
    channel.set_markup(channel.default_markup)
    if not res:
        game.take_counter = round(game.take_counter * 1.5)
        channel.add(
            "✨ На сей раз <b>вам повезло</b> и револьвер не выстрелил.\n"
            f"🃏 Следующий игрок берёт <b>{game.take_counter} карт</b>!\n"
        )
        await channel.send()
        if game.player != player:
            game.set_current_player(player)
        game.next_turn()
        game.state = GameState.SHOTGUN
    else:
        if game.player == player:
            channel.add("😴 На этом игра для вас <b>закончилась</b>.\n")
        else:
            channel.add(f"😴 {player.name} попал под пулю..\n")
        sm.leave(player)
