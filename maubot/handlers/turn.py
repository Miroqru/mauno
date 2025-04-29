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

from mau.deck.generator import card_from_str
from mau.enums import CardColor, GameState
from mau.game.game import UnoGame
from mau.game.player import Player
from maubot import markups
from maubot.filters import NowPlaying

router = Router(name="Turn")

# Обработчики
# ===========


@router.inline_query()
async def inline_handler(
    query: InlineQuery, game: UnoGame | None, player: Player | None
) -> None:
    """Обработчик inline запросов. Предоставляет клавиатуру со всеми картами."""
    if game is None or player is None or query.from_user is None:
        await query.answer(
            [markups.NO_GAME_QUERY],
            cache_time=0,
            is_personal=True,
        )
    else:
        await query.answer(
            list(markups.hand_query(player)),
            cache_time=0,
            is_personal=True,
        )


@router.chosen_inline_result(NowPlaying())
async def process_card_handler(
    result: ChosenInlineResult, game: UnoGame, player: Player
) -> None:
    """Обрабатывает все выбранные события от бота."""
    logger.info("Process result {} in game {}", result, game)
    if result.result_id in ("status", "nogame") or re.match(
        r"status:\d", result.result_id
    ):
        return None

    if player != game.player:
        game.pm.set_cp(player)

    elif result.result_id == "next":
        game.next_turn()

    elif result.result_id == "take":
        player.call_take_cards()

    elif result.result_id == "bluff":
        player.call_bluff()

    card = card_from_str(result.result_id)
    if card is not None:
        game.process_turn(card, player)


@router.callback_query(
    F.data.regexp(r"color:([0-3])").as_("color"), NowPlaying()
)
async def choose_color_call(
    query: CallbackQuery, game: UnoGame, color: re.Match[str]
) -> None:
    """Игрок выбирает цвет по нажатию на кнопку."""
    card_color = CardColor(int(color.groups()[0]))
    game.choose_color(card_color)
    await query.answer(f"🎨 Вы выбрали {card_color}.")


@router.callback_query(
    F.data.regexp(r"select_player:(\d)").as_("index"), NowPlaying()
)
async def select_player_call(
    query: CallbackQuery, game: UnoGame, player: Player, index: re.Match[str]
) -> None:
    """Действие при выборе игрока для обмена картами."""
    other_player = game.pm.get(index.groups()[0])
    if game.state == GameState.TWIST_HAND:
        player.twist_hand(other_player)

    elif query.message is not None:
        query.message.answer("🍻 Что-то пошло не так, но мы не знаем что.")

    await query.answer(f"🤝 Вы обменялись с {other_player}.")
