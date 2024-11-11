from datetime import datetime

from loguru import logger

import maubot.uno.card as c
from maubot.config import WAITING_TIME
from maubot.uno.errors import DeckEmptyError


class Player(object):
    """Represents a player.

    It is basically a doubly-linked ring list with the option to reverse the
    direction. On initialization, it will connect itself to a game and its
    other players by placing itself behind the current player.
    """

    def playable_cards(self):
        """Return a list of the cards this player can play right now."""
        playable = []
        last = self.game.last_card

        logger.debug("Last card was {}", last)

        cards = self.cards
        if self.drew:
            cards = self.cards[-1:]

        # You may only play a +4 if you have no cards of the correct color
        self.bluffing = False
        for card in cards:
            if self._card_playable(card):
                logger.debug("Matching!")
                playable.append(card)

                self.bluffing = (self.bluffing or card.color == last.color)

        # You may not play a chooser or +4 as your last card
        if len(self.cards) == 1 and self.cards[0].special:
            return list()

        return playable

    def _card_playable(self, card):
        """Check a single card if it can be played."""
        is_playable = True
        last = self.game.last_card
        logger.debug("Checking card {}", card)

        if (card.color != last.color and card.value != last.value and
                not card.special):
            logger.debug("Card's color or value doesn't match")
            is_playable = False
        elif last.value == c.DRAW_TWO and not \
                card.value == c.DRAW_TWO and self.game.draw_counter:
            logger.debug("Player has to draw and can't counter")
            is_playable = False
        elif last.special == c.DRAW_FOUR and self.game.draw_counter:
            logger.debug("Player has to draw and can't counter")
            is_playable = False
        elif (
            last.special in (c.CHOOSE, c.DRAW_FOUR)
            and card.special in (c.CHOOSE, c.DRAW_FOUR)
        ):
            logger.debug("Can't play colorchooser on another one")
            is_playable = False
        elif not last.color:
            logger.debug("Last card has no color")
            is_playable = False

        return is_playable
