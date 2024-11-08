from datetime import datetime

from loguru import logger

import maubot.card as c
from maubot.config import (
    ADMIN_LIST,
    DEFAULT_GAMEMODE,
    ENABLE_TRANSLATIONS,
    OPEN_LOBBY,
)
from maubot.deck import Deck


class Game(object):
    """Represents a game of UNO."""

    def __init__(self, chat):
        self.chat = chat
        self.last_card = None

        self.deck = Deck()

        # Game params
        self.current_player = None
        self.reversed = False
        self.choosing_color = False
        self.started = False
        self.draw_counter = 0
        self.players_won = 0
        self.starter = None
        self.mode = DEFAULT_GAMEMODE
        self.job = None
        self.owner = ADMIN_LIST
        self.open = OPEN_LOBBY
        self.translate = ENABLE_TRANSLATIONS

    @property
    def players(self):
        """Returns a list of all players in this game."""
        players = []
        if not self.current_player:
            return players

        current_player = self.current_player
        itplayer = current_player.next
        players.append(current_player)
        while itplayer and itplayer != current_player:
            players.append(itplayer)
            itplayer = itplayer.next
        return players

    def start(self):
        logger.info("Start new game in chat")
        if self.mode is None or self.mode != "wild":
            self.deck._fill_classic_()
        else:
            self.deck._fill_wild_()

        self._first_card_()
        self.started = True

    def set_mode(self, mode):
        self.mode = mode

    def reverse(self):
        """Reverses the direction of game."""
        self.reversed = not self.reversed

    def turn(self):
        """Mark the turn as over and change the current player."""
        logger.info("Next Player")
        self.current_player = self.current_player.next
        self.current_player.drew = False
        self.current_player.turn_started = datetime.now()
        self.choosing_color = False

    def _first_card_(self):
        # In case that the player did not select a game mode
        if not self.deck.cards:
            self.set_mode(DEFAULT_GAMEMODE)

        # The first card should not be a special card
        while not self.last_card or self.last_card.special:
            self.last_card = self.deck.draw()
            # If the card drawn was special, return it to the deck and loop again
            if self.last_card.special:
                self.deck.dismiss(self.last_card)

        self.play_card(self.last_card)

    def play_card(self, card):
        """Plays a card and triggers its effects.

        Should be called only from Player.play or on game start to play the
        first card.
        """
        self.deck.dismiss(self.last_card)
        self.last_card = card

        logger.info("Playing card {}", card)
        if card.value == c.SKIP:
            self.turn()
        elif card.special == c.DRAW_FOUR:
            self.draw_counter += 4
            logger.debug("Draw counter increased by 4")
        elif card.value == c.DRAW_TWO:
            self.draw_counter += 2
            logger.debug("Draw counter increased by 2")
        elif card.value == c.REVERSE:
            # Special rule for two players
            if self.current_player == self.current_player.next.next:
                self.turn()
            else:
                self.reverse()

        # Don't turn if the current player has to choose a color
        if card.special not in (c.CHOOSE, c.DRAW_FOUR):
            self.turn()
        else:
            logger.debug("Choosing Color...")
            self.choosing_color = True

    def choose_color(self, color):
        """Carries out the color choosing and turns the game."""
        self.last_card.color = color
        self.turn()
