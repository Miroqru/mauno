"""Представляет игроков, связанных с текущей игровой сессией."""

from typing import TYPE_CHECKING

from loguru import logger

from maubot.uno.card import BaseCard
from maubot.uno.exceptions import DeckEmptyError

if TYPE_CHECKING:
    from maubot.uno.game import UnoGame


class Player:
    """Игрок для сессии Uno.

    Каждый игрок привязывается к конкретной игровой сессии.
    Реализует команды для взаимодействия игрока с текущей сессией.
    """

    def __init__(self, game: 'UnoGame', user):
        self.hand: BaseCard = []
        self.game: 'UnoGame' = game
        self.user = user

        self.bluffing = False
        self.took_card = False
        self.anti_cheat = 0

    def take_first_hand(self):
        """Берёт начальный набор карт для игры."""
        logger.debug("{} Draw first hand for player", self.user)
        try:
            self.hand = list(self.game.deck.take(7))
        except DeckEmptyError:
            for card in self.hand:
                self.game.deck.put(card)
            logger.warning("There not enough cards in deck for player")
            raise DeckEmptyError()

    def take_cards(self):
        """Игрок берёт заданное количество карт согласно счётчику."""
        take_counter = self.game.take_counter or 1
        logger.debug("{} Draw {} cards", self.user, take_counter)

        for card in self.game.deck.take(take_counter):
            self.hand.append(card)
        self.game.take_counter = 0
        self.took_card = True

    def put_card(self, card_index: int):
        """Разыгрывает одну из карт из своей руки."""
        card = self.hand.pop(card_index)
        self.game.process_turn(card)


    # Обработка событий
    # =================

    def on_leave(self):
        """Действия игрока при выходе из игры."""
        logger.debug("{} Leave from game", self.user)
        # Если он последний игрок, подчищать за собой не приходится
        if len(self.game.players) == 1:
            return

        for card in self.hand:
            self.game.deck.put(card)
        self.hand = []


    # Магические методы
    # =================

    def __repr__(self):
        """Представление игрока при отладке."""
        return repr(self.user)

    def __str__(self):
        """Представление игрока в строковом виде."""
        return str(self.user)
