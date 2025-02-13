"""Обработка хода.

FIXME: Данный компонент достаточно сильно зависит от Telegram бота, потом был
выделен отдельно.
"""

from random import randint

from loguru import logger

from mau.card import BaseCard, CardColor, CardType
from mau.enums import GameState
from mau.game import UnoGame
from mau.player import Player
from maubot import keyboards, messages

TWIST_HAND_NUM = 2


def process_turn(game: UnoGame, card: BaseCard, player: Player) -> None:
    """Обрабатываем текущий ход."""
    logger.info("Playing card {}", card)
    game.deck.put_on_top(card)
    player.hand.remove(card)
    game.journal.set_actions(None)

    card(game)

    # 8< -------------------------

    if len(player.hand) == 1:
        game.journal.add("🌟 UNO!\n")

    if len(player.hand) == 0:
        game.journal.add(f"👑 {game.name} победил(а)!\n")
        game.remove_player(game.user.id)
        if not game.started:
            game.journal.add(messages.end_game_message(game))

    elif all(card.cost == TWIST_HAND_NUM, game.rules.twist_hand):
        game.journal.add(f"✨ {game.name} Задумывается c кем обменяться.")
        game.state = GameState.TWIST_HAND
        # TODO: update acton keyboard
        game.journal.set_actions(keyboards.select_player_markup(game))

    elif all(game.rules.rotate_cards, game.deck.top.cost == 0):
        game.rotate_cards()
        game.journal.add(
            "🤝 Все игроки обменялись картами по кругу.\n"
            f"{messages.get_room_players(game)}"
        )

    if card.card_type in (CardType.TAKE_FOUR, CardType.CHOOSE_COLOR):
        game.journal.add(f"✨ {game.name} Задумывается о выборе цвета.")
        game.state = GameState.CHOOSE_COLOR
        # TODO: update acton keyboard
        game.journal.set_actions(keyboards.COLOR_MARKUP)

    if any(
        game.rules.random_color,
        game.rules.choose_random_color,
        game.rules.auto_choose_color,
    ):
        game.journal.add(f"🎨 Текущий цвет.. {game.deck.top.color}")

    if game.state == GameState.NEXT:
        if game.rules.random_color:
            game.deck.top.color = CardColor(randint(0, 3))
        if game.deck.top.cost == 1 and game.rules.side_effect:
            logger.info("Player continue turn")
        else:
            game.next_turn()
