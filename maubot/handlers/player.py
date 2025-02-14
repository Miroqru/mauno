"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение.
"""

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger

from mau.card import TakeCard, TakeFourCard
from mau.enums import GameState
from mau.game import UnoGame
from mau.messages import end_game_message
from mau.player import BaseUser, Player
from mau.session import SessionManager
from maubot import filters, keyboards
from maubot.messages import NOT_ENOUGH_PLAYERS, get_room_status

router = Router(name="Player")

# Обработчики
# ===========


@router.message(Command("join"), filters.ActiveGame())
async def join_player(
    message: Message, sm: SessionManager, game: UnoGame, bot: Bot
) -> None:
    """Подключает пользователя к игре."""
    if message.from_user is None:
        raise ValueError("User can`t be none")

    # TODO: Предложение о глобальной обработке ошибок в силе!
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

    if not game.started:
        await bot.edit_message_text(
            text=get_room_status(game),
            chat_id=game.room_id,
            message_id=game.lobby_message,
            reply_markup=keyboards.get_room_markup(game),
        )
    else:
        game.journal.add(
            f"🍰 Добро пожаловать в игру, {message.from_user.mention_html()}!"
        )
        await game.journal.send_journal()


@router.message(Command("leave"), filters.ActivePlayer())
async def leave_player(
    message: Message,
    sm: SessionManager,
    game: UnoGame,
    player: Player,
) -> None:
    """Выход пользователя из игры."""
    sm.leave(player)

    if game.started:
        game.journal.add(
            text=(f"🍰 Ладненько, следующих ход за {game.player.name}.")
        )
        await game.journal.send_journal()
    else:
        status_message = f"{NOT_ENOUGH_PLAYERS}\n\n{end_game_message(game)}"
        sm.remove(str(message.chat.id))
        await message.answer(status_message)


# Обработчики для кнопок
# ======================


@router.callback_query(F.data == "join", filters.ActiveGame())
async def join_callback(
    query: CallbackQuery, sm: SessionManager, game: UnoGame
) -> None:
    """Добавляет игрока в текущую комнату."""
    # TODO: Тут тоже глобальный отлов ошибочек
    sm.join(
        str(query.message.chat.id),
        BaseUser(str(query.from_user.id), query.from_user.mention_html()),
    )

    if isinstance(query.message, Message):
        await query.message.edit_text(
            text=get_room_status(game),
            reply_markup=keyboards.get_room_markup(game),
        )


@router.callback_query(F.data == "take", filters.NowPlaying())
async def take_cards_call(
    query: CallbackQuery,
    sm: SessionManager,
    game: UnoGame,
    player: Player,
) -> None:
    """Игрок выбирает взять карты."""
    if game.player == player:
        game.journal.add("🃏 Вы решили что будет проще <b>взять карты</b>.")
    else:
        game.set_current_player(player)
        game.journal.add(f"🃏 Некто {player.name} решили <b>взять карты</b>.")

    player.take_cards()
    if len(player.game.deck.cards) == 0:
        game.journal.add(
            "🃏 В колоде не осталось карт для игрока.",
        )

    # Если пользователь сам взял карты, то не нужно пропускать ход
    if isinstance(game.deck.top, TakeCard | TakeFourCard) and game.take_counter:
        game.next_turn()
        game.journal.add(f"🍰 <b>Следующий ходит</b>: {game.player.name}")
    else:
        game.journal.add(f"☕ {game.player.name} <b>продолжает</b>.")
    await game.journal.send_journal()


@router.callback_query(F.data == "shot", filters.NowPlaying())
async def shotgun_call(
    query: CallbackQuery,
    sm: SessionManager,
    game: UnoGame,
    player: Player,
) -> None:
    """Игрок выбирает взять карты."""
    res = player.shotgun()
    game.journal.set_actions(None)
    if not res:
        game.take_counter = round(game.take_counter * 1.5)
        game.journal.add(
            "✨ На сей раз <b>вам повезло</b> и револьвер не выстрелил.",
        )
        game.journal.add(
            f"🃏 Следующий игрок берёт <b>{game.take_counter} карт</b>!\n",
        )
        await game.journal.send_journal()
        if game.player != player:
            game.set_current_player(player)
        game.next_turn()
        game.state = GameState.SHOTGUN
    else:
        if game.player == player:
            game.journal.add("😴 На этом игра для вас <b>закончилась</b>.\n")
        else:
            game.journal.add(f"😴 {player.name} попал под пулю..\n")

        await game.journal.send_journal()
        sm.leave(player)

    if game.started:
        game.journal.add(f"🍰 Ладненько, следующим ходит {game.player.name}.")
        await game.journal.send_journal()
    else:
        status = end_game_message(game)
        sm.remove(game.room_id)
        if isinstance(query.message, Message):
            await query.message.edit_text(text=status)
