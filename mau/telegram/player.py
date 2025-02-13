"""Обработка взятие карт.

FIXME: Зависит от Telegram клавиатуры.
"""

from loguru import logger

from mau.card import TakeCard, TakeFourCard
from mau.enums import GameState
from mau.player import Player
from maubot import keyboards

_MIN_SHOTGUN_TAKE_COUNTER = 3


async def call_take_cards(player: Player) -> None:
    """Действия игрока при взятии карты.

    В зависимости от правил, можно взять не одну карту, а сразу
    несколько.
    Если включен револьвер, то при взятии нескольких карт будет
    выбор:

    - Брать карты сейчас.
    - Выстрелить, чтобы взял следующий игрок.
    """
    if player.game.rules.take_until_cover and player.game.take_counter == 0:
        player.game.take_counter = player.game.deck.count_until_cover()
        player.game.journal.add(f"🍷 беру {player.game.take_counter} карт.\n")

    if any(
        player.game.take_counter > _MIN_SHOTGUN_TAKE_COUNTER,
        player.game.rules.shotgun,
        player.game.rules.single_shotgun,
    ):
        current = (
            player.game.shotgun_current
            if player.game.rules.single_shotgun
            else player.shotgun_current
        )
        player.game.journal.add(
            "💼 У нас для Вас есть <b>деловое предложение</b>!\n\n"
            f"Вы можете <b>взять свои карты</b> "
            "или же попробовать <b>выстрелить из револьвера</b>.\n"
            "Если вам повезёт, то карты будет брать уже следующий игрок.\n"
            f"🔫 Из револьвера стреляли {current} / 8 раз\n."
        )
        player.game.journal.set_actions(keyboards.SHOTGUN_REPLY)

    logger.info("{} take cards", player)
    take_counter = player.game.take_counter
    player.take_cards()
    if len(player.game.deck.cards) == 0:
        player.game.journal.add("🃏 В колоде не осталось карт для игрока.")

    # Если пользователь выбрал взять карты, то он пропускает свой ход
    if (
        isinstance(player.game.deck.top, TakeCard | TakeFourCard)
        and take_counter
    ):
        player.game.next_turn()
    else:
        player.game.state = GameState.NEXT
