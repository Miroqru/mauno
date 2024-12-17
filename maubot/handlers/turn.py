"""Обрабатывает действия игрока во время хода.

Это касается обработки Inline query и при помощи него результатов.
"""

import re

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from maubot import keyboards, messages
from maubot.stickers import from_str
from maubot.uno.card import (
    BaseCard,
    CardColor,
    CardType,
    TakeCard,
    TakeFourCard,
)
from maubot.uno.enums import GameState
from maubot.uno.game import UnoGame
from maubot.uno.player import Player
from maubot.uno.session import SessionManager

router = Router(name="Turn")

# Дополнительные функции
# ======================

async def take_card(player: Player) -> str | None:
    """Действие при взятии карты пользователем."""
    logger.info("{} take cards", player)
    take_counter = player.game.take_counter
    player.take_cards()
    if len(player.game.deck.cards) == 0:
        player.game.journal.add("🃏 В колоде не осталось карт для игрока.")

    # Если пользователь выбрал взять карты, то он пропускает свой ход
    if (isinstance(player.game.deck.top, (TakeCard, TakeFourCard))
        and take_counter
    ):
        await player.game.next_turn()
    else:
        player.game.state = GameState.NEXT
    return None

def call_bluff(player: Player) -> str:
    """Проверка на честность предыдущего игрока."""
    logger.info("{} call bluff", player)
    bluff_player = player.game.bluff_player
    if bluff_player.bluffing:
        player.game.journal.add((
            "🔎 <b>Замечен блеф</b>!\n"
            f"{bluff_player.user.first_name} получает "
            f"{player.game.take_counter} карт."
        ))
        bluff_player.take_cards()

        if len(player.game.deck.cards) == 0:
            player.game.journal.add("🃏 В колоде не осталось свободных карт.")
    else:
        player.game.take_counter += 2
        player.game.journal.add((
            f"🎩 {bluff_player.user.first_name} <b>Честный игрок</b>!\n"
            f"{player.user.first_name} получает "
            f"{player.game.take_counter} карт.\n"
        ))
        player.take_cards()
        if len(player.game.deck.cards) == 0:
            player.game.journal.add("🃏 В колоде не осталось свободных карт.")

async def play_card(player: Player, card: BaseCard) -> str:
    """Разыгрывает выброшенную карту."""
    logger.info("Push {} from {}", card, player.user.id)
    player.hand.remove(card)
    await player.game.process_turn(card)
    player.game.journal.set_markup(None)

    if len(player.hand) == 1:
        player.game.journal.add("🌟 UNO!\n")

    if len(player.hand) == 0:
        player.game.journal.add(f"👑 {player.user.first_name} победил(а)!\n")
        player.game.winners.append(player)
        await player.game.remove_player(player.user.id)

        if not player.game.started:
            player.game.journal.add(messages.end_game_message(player.game))

    elif card.cost == 2 and player.game.rules.twist_hand:
        player.game.journal.add(
            f"✨ {player.name} Задумывается c кем обменяться."
        )
        player.game.journal.set_markup(keyboards.select_player_markup(player))

    elif (player.game.rules.rotate_cards
        and player.game.deck.top.cost == 0
        and len(player.hand) > 0
    ):
        player.game.journal.add((
            "🤝 Все игроки обменялись картами по кругу.\n"
            f"{messages.get_room_players(player.game)}"
        ))

    if card.card_type in (
        CardType.TAKE_FOUR, CardType.CHOOSE_COLOR
    ):
        player.game.journal.add(
            f"✨ {player.name} Задумывается о выборе цвета."
        )
        player.game.journal.set_markup(keyboards.COLOR_MARKUP)

    if (player.game.rules.random_color
        or player.game.rules.choose_random_color
        or player.game.rules.auto_choose_color
    ):
        player.game.journal.add(
            f"🎨 Я выбираю цвет.. {player.game.deck.top.color}"
        )


# Обработчики
# ===========

@router.inline_query()
async def inline_handler(query: InlineQuery,
    game: UnoGame | None,
    player: Player | None
):
    """Обработчик inline запросов к бот."""
    if game is None or player is None:
        result = keyboards.NO_GAME_QUERY
    else:
        result = keyboards.get_hand_query(game.get_player(query.from_user.id))

    await query.answer(result, cache_time=1, is_personal=True)

@router.chosen_inline_result()
async def process_card_handler(result: ChosenInlineResult,
    game: UnoGame | None,
    player: Player | None,
    bot: Bot,
    sm: SessionManager
):
    """Обрабатывает все выбранные события от бота."""
    logger.info("Process result {} in game {}", result, game)
    # Пропускаем если нам передали не действительные значения игрока и игры
    # Нам не нужно повторно отправлять сообщения если это статус игры
    if (player is None
        or game is None
        or result.result_id in ("status", "nogame")
        or re.match(r"status:\d", result.result_id)
    ):
        return

    game.journal.set_markup(keyboards.TURN_MARKUP)

    if result.result_id == "pass":
        await game.next_turn()

    elif result.result_id == "take":
        if game.rules.take_until_cover and game.take_counter == 0:
            game.take_counter = game.deck.count_until_cover()
            game.journal.add(f"🍷 беру {game.take_counter} карт.\n")
        if not game.rules.shotgun and not game.rules.single_shotgun:
            await take_card(player)
        elif game.take_counter <= 2 or game.state == GameState.SHOTGUN:
            await take_card(player)
        else:
            current = (
                game.shotgun_current if game.rules.single_shotgun
                else player.shotgun_current
            )
            game.journal.add((
                "💼 У нас для Вас есть <b>деловое предложение</b>!\n\n"
                f"Вы можете <b>взять свои карты</b> "
                "или же попробовать <b>выстрелить из револьвера</b>.\n"
                "Если вам повезёт, то карты будет брать уже следующий игрок.\n"
                f"🔫 Из револьвера стреляли {current} / 8 раз\n."
            ))
            game.journal.set_markup(keyboards.SHOTGUN_REPLY)

    elif result.result_id == "bluff":
        call_bluff(player)
        await game.journal.send_journal()
        await game.next_turn()

    change_color = re.match(r"color:([0-3])", result.result_id)
    if change_color is not None:
        await game.choose_color(CardColor(int(change_color.groups()[0])))

    select_player = re.match(r"select_player:(\d)", result.result_id)
    if select_player is not None:
        other_player = game.players[int(select_player.groups()[0])]
        if game.state == GameState.TWIST_HAND:
            player_hand = len(player.hand)
            other_hand = len(other_player.hand)
            game.journal.add((
                f"🤝 {player.user.first_name} ({player_hand} карт) "
                f"и {other_player.user.first_name} ({other_hand} карт) "
                "обменялись руками.\n"
            ))
            player.twist_hand(other_player)
        else:
            game.journal.add("🍻 Что-то пошло не так, но мы не знаем что.")

    card = from_str(result.result_id)
    if card is not None:
        await play_card(player, card)

    if game.state == GameState.NEXT:
        game.journal.add(
            f"🍰 <b>Следующий ходит</b>: {game.player.name}"
        )
        if game.journal.reply_markup is None:
            game.journal.set_markup(keyboards.TURN_MARKUP)
    await game.journal.send_journal()


# Обработчики для кнопок
# ======================

@router.callback_query(F.data.regexp(r"color:([0-3])").as_("color"))
async def choose_color_call( # noqa
    query: CallbackQuery,
    game: UnoGame | None,
    player: Player | None,
    color: re.Match[str],
    sm: SessionManager,
    bot: Bot
):
    """Выбирает цвет по нажатию на кнопку."""
    if game is None or player is None:
        return await query.answer("🍉 А вы точно сейчас играете?")
    if not game.rules.ahead_of_curve and game.player != player:
        return await query.answer("🍉 А вы точно сейчас ходите?")

    color = CardColor(int(color.groups()[0]))
    game.journal.add(f"🎨 Я выбираю цвет.. {color}\n")
    game.journal.set_markup(None)
    await game.journal.send_journal()
    await game.choose_color(color)

    if game.started:
        game.journal.add(
            f"🍰 <b>Следующий ходит</b>: {game.player.name}"
        )
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        sm.remove(player.game.chat_id)

    return await query.answer(f"🎨 Вы выбрали {color}.")

@router.callback_query(F.data.regexp(r"select_player:(\d)").as_("index"),)
async def select_player_call(query: CallbackQuery,
    game: UnoGame | None,
    player: Player | None,
    index: re.Match[int]
):
    if game is None or player is None:
        return await query.answer("🍉 А вы точно сейчас играете?")
    if not game.rules.ahead_of_curve and game.player != player:
        return await query.answer("🍉 А вы точно сейчас ходите?")

    other_player = game.players[int(index.groups()[0])]
    if game.state == GameState.TWIST_HAND:
        player_hand = len(player.hand)
        other_hand = len(other_player.hand)
        game.journal.add((
            f"🤝 {player.user.first_name} ({player_hand} карт) "
            f"и {other_player.user.first_name} ({other_hand} карт) "
            "обменялись руками.\n"
        ))
        game.journal.set_markup(None)
        await game.journal.send_journal()
        player.twist_hand(other_player)
    else:
        game.journal.add("🍻 Что-то пошло не так, но мы не знаем что.")

    game.journal.add(
        f"🍰 <b>Следующий ходит</b>: {game.player.name}"
    )
    game.journal.set_markup(keyboards.TURN_MARKUP)
    await game.journal.send_journal()
