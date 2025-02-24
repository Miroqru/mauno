"""Обрабатывает действия игрока во время хода.

Это касается обработки Inline query и при помощи него результатов.
"""

import re

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    ChosenInlineResult,
    InlineQuery,
)
from loguru import logger

from mau.card import CardColor, card_from_str
from mau.enums import GameState
from mau.game import UnoGame
from mau.player import Player
from maubot import keyboards
from maubot.events.journal import MessageJournal
from maubot.filters import NowPlaying

router = Router(name="Turn")

# Обработчики
# ===========


@router.inline_query()
async def inline_handler(
    query: InlineQuery, game: UnoGame | None, player: Player | None
) -> None:
    """Обработчик inline запросов к боту.

    Здесь предоставляется клавиатура со всеми вашими картами.
    """
    if game is None or player is None or query.from_user is None:
        res = keyboards.NO_GAME_QUERY
    else:
        res = keyboards.get_hand_query(player)

    await query.answer(list(res), cache_time=1, is_personal=True)


@router.chosen_inline_result()
async def process_card_handler(
    result: ChosenInlineResult,
    game: UnoGame | None,
    player: Player | None,
    journal: MessageJournal,
) -> None:
    """Обрабатывает все выбранные события от бота."""
    logger.info("Process result {} in game {}", result, game)
    # Пропускаем если нам передали не действительные значения игрока и игры
    # Нам не нужно повторно отправлять сообщения если это статус игры
    if (
        player is None
        or game is None
        or result.result_id in ("status", "nogame")
        or re.match(r"status:\d", result.result_id)
    ):
        return None

    if player != game.player:
        game.set_current_player(player)

    elif result.result_id == "pass":
        game.next_turn()

    elif result.result_id == "take":
        player.call_take_cards()

    elif result.result_id == "bluff":
        player.call_bluff()

    change_color = re.match(r"color:([0-3])", result.result_id)
    if change_color is not None:
        game.choose_color(CardColor(int(change_color.groups()[0])))

    select_player = re.match(r"select_player:(\d)", result.result_id)
    if select_player is not None:
        if game.state == GameState.TWIST_HAND:
            other_player = game.players[int(select_player.groups()[0])]
            player.twist_hand(other_player)
        else:
            journal.add("🍻 Что-то пошло не так, но мы не знаем что.")

    card = card_from_str(result.result_id)
    if card is not None:
        game.process_turn(card, player)

        # if game.started and game.state == GameState.NEXT:
        #     journal.add("🌀 Продолжаем ход")
    # await journal.send()


# Обработчики для кнопок
# ======================


@router.callback_query(
    F.data.regexp(r"color:([0-3])").as_("color"), NowPlaying()
)
async def choose_color_call(
    query: CallbackQuery,
    game: UnoGame,
    player: Player,
    color: re.Match[str],
    journal: MessageJournal,
) -> None:
    """Игрок выбирает цвет по нажатию на кнопку."""
    card_color = CardColor(int(color.groups()[0]))

    # Поскольку цвет уже выбран, нам бы убрать клавиатуру
    game.choose_color(card_color)
    await query.answer(f"🎨 Вы выбрали {card_color}.")


@router.callback_query(
    F.data.regexp(r"select_player:(\d)").as_("index"), NowPlaying()
)
async def select_player_call(
    query: CallbackQuery,
    game: UnoGame,
    player: Player,
    index: re.Match,
    journal: MessageJournal,
) -> None:
    """Действие при выборе игрока для обмена картами."""
    other_player = game.players[int(index.groups()[0])]
    if game.state == GameState.TWIST_HAND:
        player.twist_hand(other_player)
    else:
        journal.add("🍻 Что-то пошло не так, но мы не знаем что.")
        await journal.send_journal()

    await query.answer(f"🤝 Вы обменялись с {other_player}.")
