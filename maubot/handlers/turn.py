"""Обрабатывает действия игрока во время хода.

Это касается обработки Inline query и при помощи него результатов.
"""

import re

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from mau.card import CardColor, card_from_str
from mau.enums import GameState
from mau.game import UnoGame
from mau.player import Player
from mau.session import SessionManager
from mau.telegram.player import call_take_cards
from mau.telegram.turn import process_turn
from maubot import keyboards

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
    if game is None or player is None:
        result = keyboards.NO_GAME_QUERY
    else:
        result = keyboards.get_hand_query(game.get_player(query.from_user.id))

    await query.answer(result, cache_time=1, is_personal=True)


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
    if any(
        player is None,
        game is None,
        result.result_id in ("status", "nogame"),
        re.match(r"status:\d", result.result_id),
    ):
        return

    if player != game.player:
        game.journal.add(f"😈 {player.name} вмешался в игру.")
        game.set_current_player(player)

    if result.result_id == "pass":
        game.next_turn()

    elif result.result_id == "take":
        call_take_cards(player)

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
        process_turn(game, card, player)

    if game.started and game.state == GameState.NEXT:
        game.journal.add(
            "🌀 Продолжаем ход"
            if game.player == player
            else f"🍰 <b>Следующий ходит</b>: {game.player.name}"
        )
        if game.journal.reply_markup is None:
            game.journal.set_actions(keyboards.TURN_MARKUP)

    await game.journal.send_journal()


# Обработчики для кнопок
# ======================


@router.callback_query(F.data.regexp(r"color:([0-3])").as_("color"))
async def choose_color_call(  # noqa
    query: CallbackQuery,
    game: UnoGame | None,
    player: Player | None,
    color: re.Match[str],
    sm: SessionManager,
    bot: Bot,
) -> None:
    """Игрок выбирает цвет по нажатию на кнопку."""
    if game is None or player is None:
        return await query.answer("🍉 А вы точно сейчас играете?")
    if not game.rules.ahead_of_curve and game.player != player:
        return await query.answer("🍉 А вы точно сейчас ходите?")

    color = CardColor(int(color.groups()[0]))
    game.journal.add(f"🎨 Я выбираю цвет.. {color}\n")
    game.journal.set_actions(None)
    await game.journal.send_journal()
    game.choose_color(color)

    if game.started:
        game.journal.add(f"🍰 <b>Следующий ходит</b>: {game.player.name}")
        game.journal.set_actions(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        sm.remove(player.game.chat_id)

    return await query.answer(f"🎨 Вы выбрали {color}.")


@router.callback_query(
    F.data.regexp(r"select_player:(\d)").as_("index"),
)
async def select_player_call(
    query: CallbackQuery,
    game: UnoGame | None,
    player: Player | None,
    index: re.Match[int],
) -> None:
    """Действие при выборе игрока для обмена картами."""
    if game is None or player is None:
        return await query.answer("🍉 А вы точно сейчас играете?")
    if not game.rules.ahead_of_curve and game.player != player:
        return await query.answer("🍉 А вы точно сейчас ходите?")

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
    game.journal.set_actions(keyboards.TURN_MARKUP)
    await game.journal.send_journal()
