"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение.
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

from maubot import keyboards, messages
from maubot.messages import (
    NO_ROOM_MESSAGE,
    NOT_ENOUGH_PLAYERS,
    get_closed_room_message,
    get_room_status,
)
from maubot.uno.card import TakeCard, TakeFourCard
from maubot.uno.enums import GameState
from maubot.uno.exceptions import (
    AlreadyJoinedError,
    DeckEmptyError,
    LobbyClosedError,
    NoGameInChatError,
)
from maubot.uno.game import UnoGame
from maubot.uno.player import Player
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
        await message.answer(NO_ROOM_MESSAGE)
    except LobbyClosedError:
        await message.answer(get_closed_room_message(game))
    except AlreadyJoinedError:
        await message.answer("🍰 Вы уже с нами в комнате.")
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

    if game is not None:
        if not game.started:
            await bot.edit_message_text(
                text=get_room_status(game),
                chat_id=game.chat_id,
                message_id=game.lobby_message,
                reply_markup=keyboards.get_room_markup(game)
            )
        else:
            game.journal.add(
                "🍰 Добро пожаловать в игру, "
                f"{message.from_user.mention_html()}!"
            )
            await game.journal.send_journal()

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
        game.journal.add(text=(
            "🍰 Ладненько, следующих ход за "
            f"{game.player.user.mention_html()}."
        ))
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        status_message = (
            f"{NOT_ENOUGH_PLAYERS}\n\n{messages.end_game_message(game)}"
        )
        sm.remove(message.chat.id)
        await message.answer(status_message)


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
        await query.message.answer(get_closed_room_message(game))
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

@router.callback_query(F.data=="take")
async def take_cards_call(query: CallbackQuery,
    sm: SessionManager,
    game: UnoGame |  None,
    player: Player | None
):
    """Игрок выбирает взять карты."""
    if game is None or player is None:
        return await query.answer("🍉 А вы точно сейчас играете?")
    if not game.rules.ahead_of_curve and game.player != player:
        return await query.answer("🍉 А вы точно сейчас ходите?")

    take_counter = game.take_counter
    game.journal.set_markup(None)
    game.journal.add("🃏 Вы решили что будет проще <b>взять карты</b>.")
    player.take_cards()

    if len(player.game.deck.cards) == 0:
        game.journal.add("🃏 В колоде не осталось карт для игрока.",)

    # Если пользователь сам взял карты, то не нужно пропускать ход
    if (isinstance(game.deck.top, (TakeCard, TakeFourCard))
        and take_counter
    ):
        game.next_turn()

    game.journal.add(
        f"🍰 <b>Следующий ходит</b>: {game.player.user.mention_html()}"
    )
    game.journal.set_markup(keyboards.TURN_MARKUP)
    await game.journal.send_journal()

@router.callback_query(F.data=="shot")
async def shotgun_call(query: CallbackQuery,
    sm: SessionManager,
    game: UnoGame |  None,
    player: Player | None
):
    """Игрок выбирает взять карты."""
    if game is None or player is None:
        return await query.answer("🍉 А вы точно сейчас играете?")
    if not game.rules.ahead_of_curve and game.player != player:
        return await query.answer("🍉 А вы точно сейчас ходите?")

    res = player.shotgun()
    game.journal.set_markup(None)
    if not res:
        game.take_counter = round(game.take_counter*1.5)
        game.journal.add(
            "✨ На этот раз <b>вам повезло</b> и пистолет не выстрелил.",
        )
        game.journal.add(
            f"🃏 Следующий игрок берёт <b>{game.take_counter} карт</b>!\n",
        )
        await game.journal.send_journal()
        game.next_turn()
        game.state = GameState.SHOTGUN
    else:
        game.journal.add("😴 На этом игра для вас <b>закончилась</b>.\n")
        await game.journal.send_journal()
        game.remove_player(query.from_user.id)
        chat_id = sm.user_to_chat.pop(query.from_user.id)

    if game.started:
        game.journal.add(
            f"🍰 Ладненько, следующим ходит {game.player.user.mention_html()}."
        )
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        status = messages.end_game_message(game)
        sm.remove(chat_id)
        await query.message.edit_text(text=status)



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
        game.journal.add(
           f"Ладненько, следующих ход за {game.player.user.mention_html()}."
        )
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        status_message = NOT_ENOUGH_PLAYERS
        sm.remove(event.chat.id)
        await event.answer(status_message)

