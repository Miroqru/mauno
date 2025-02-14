"""Обрабатывает действия игрока во время хода.

Это касается обработки Inline query и при помощи него результатов.
"""

import re

from aiogram import Bot, F, Router
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
from mau.session import SessionManager
from maubot import keyboards
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
    bot: Bot,
    sm: SessionManager,
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
        game.journal.add(f"😈 {player.name} вмешался в игру.")
        game.set_current_player(player)

    if result.result_id == "pass":
        game.next_turn()

    elif result.result_id == "take":
        await player.call_take_cards()

    elif result.result_id == "bluff":
        await player.call_bluff()

    change_color = re.match(r"color:([0-3])", result.result_id)
    if change_color is not None:
        game.choose_color(CardColor(int(change_color.groups()[0])))

    select_player = re.match(r"select_player:(\d)", result.result_id)
    if select_player is not None:
        other_player = game.players[int(select_player.groups()[0])]
        if game.state == GameState.TWIST_HAND:
            player_hand = len(player.hand)
            other_hand = len(other_player.hand)
            game.journal.add(
                f"🤝 {player.name} ({player_hand} карт) "
                f"и {other_player.name} ({other_hand} карт) "
                "обменялись руками.\n"
            )
            player.twist_hand(other_player)
        else:
            game.journal.add("🍻 Что-то пошло не так, но мы не знаем что.")

    card = card_from_str(result.result_id)
    if card is not None:
        game.process_turn(card, player)

    if game.started and game.state == GameState.NEXT:
        game.journal.add(
            "🌀 Продолжаем ход"
            if game.player == player
            else f"🍰 <b>Следующий ходит</b>: {game.player.name}"
        )

    await game.journal.send_journal()


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
) -> None:
    """Игрок выбирает цвет по нажатию на кнопку."""
    card_color = CardColor(int(color.groups()[0]))
    game.choose_color(card_color)
    game.journal.add(f"🎨 Я выбираю цвет.. {card_color}\n")
    game.journal.add(f"🍰 <b>Следующий ходит</b>: {game.player.name}")
    await game.journal.send_journal()
    await query.answer(f"🎨 Вы выбрали {card_color}.")


@router.callback_query(
    F.data.regexp(r"selecNowPlayingt_player:(\d)").as_("index"), NowPlaying()
)
async def select_player_call(
    query: CallbackQuery,
    game: UnoGame,
    player: Player,
    index: re.Match,
) -> None:
    """Действие при выборе игрока для обмена картами."""
    other_player = game.players[int(index.groups()[0])]
    if game.state == GameState.TWIST_HAND:
        player_hand = len(player.hand)
        other_hand = len(other_player.hand)
        game.journal.add(
            f"🤝 {player.name} ({player_hand} карт) "
            f"и {other_player.name} ({other_hand} карт) "
            "обменялись руками.\n"
        )
        game.journal.set_actions(None)
        await game.journal.send_journal()
        player.twist_hand(other_player)
    else:
        game.journal.add("🍻 Что-то пошло не так, но мы не знаем что.")

    game.journal.add(f"🍰 <b>Следующий ходит</b>: {game.player.name}")
    await game.journal.send_journal()
    await query.answer(f"🤝 Вы обменялись с {other_player}.")
