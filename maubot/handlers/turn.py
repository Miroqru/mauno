"""Обрабатывает действия игрока во время хода.

Это касается обработки Inline query и при помощи него результатов.
"""

import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery

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
    card = card_from_str(result.result_id)
    if card is not None:
        game.process_turn(card, player)


# TODO: Вернуть методы на место


@router.callback_query(F.data == "next", NowPlaying())
async def call_next(query: CallbackQuery, game: UnoGame) -> None:
    """Передаёт ход следующему игроку."""
    game.next_turn()


@router.callback_query(F.data == "take", NowPlaying())
async def call_take(query: CallbackQuery, player: Player) -> None:
    """Берёт карты."""
    player.call_take_cards()


@router.callback_query(F.data == "bluff", NowPlaying())
async def call_bluff(query: CallbackQuery, player: Player) -> None:
    """Проверка игрока на честность."""
    player.call_bluff()


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
    F.data.regexp(r"select_player:(\d+)").as_("user_id"), NowPlaying()
)
async def select_player_call(
    query: CallbackQuery, game: UnoGame, player: Player, user_id: re.Match[str]
) -> None:
    """Действие при выборе игрока для обмена картами."""
    other_player = game.pm.get(user_id.groups()[0])
    if game.state == GameState.TWIST_HAND:
        player.twist_hand(other_player)

    elif query.message is not None:
        query.message.answer("🍻 Что-то пошло не так, но мы не знаем что.")

    await query.answer(f"🤝 Вы обменялись с {other_player}.")
