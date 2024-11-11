"""Игровая сессия.

Представляет класс игровой сессии.
Иначе говоря игровой движок, обрабатывающий ходы игроков и
действия карт из колоды.
"""

from datetime import datetime
from random import shuffle
from typing import NamedTuple

from loguru import logger

from maubot.uno.card import BaseCard, CardColor
from maubot.uno.deck import Deck


class GameRules(NamedTuple):
    """Набор игровых правил, которые можно менять при запуске игры."""

    timer: bool
    wild: bool


class UnoGame:
    """Представляет каждую игру Uno.

    Каждая отдельная игра привязывается к конкретному чату.
    Предоставляет методы для обработки карт и очерёдности ходов.
    """

    def __init__(self, chat_id: int, rules: GameRules):
        self.chat_id = chat_id
        self.rules = rules
        self.deck = Deck()

        # Игроки Uno
        # TODO: Тип игрока
        self.current_player: int = 0
        self.start_player = None
        self.players = []
        self.winners = []

        # Настройки игры
        self.started: bool = False
        self.open: bool = True
        self.reverse: bool = False
        self.choose_color_flag: bool = False
        self.take_counter: int = 0

        # Таймеры
        self.game_start = datetime.now()
        self.turn_start = datetime.now()

    # TODO: Тип игрока
    @property
    def player(self):
        """Возвращает текущего игрока."""
        return self.players[self.current_player]


    def get_player(self, user_id: int):
        for player in self.players:
            if player.user.id == user_id:
                return player
        return None


    # Управление потоком игры
    # =======================

    def start(self) -> None:
        """Начинает новую игру в чате."""
        logger.info("Start new game in chat {}", self.chat_id)
        self.started = True
        shuffle(self.players)

        if self.rules.wild:
            self.deck.fill_wild()
        else:
            self.deck.fill_classic()

        self.take_first_card()

    def take_first_card(self):
        """Берёт первую карту для начали игры."""
        # TODO: Описание карт
        while self.deck.top is None or self.deck.top.color == CardColor.BLACK:
            card = self.deck.take_one()
            if card.color == CardColor.BLACK:
                self.deck.put(card)
            else:
                self.deck.put_on_top(card)

        self.deck.top(self)

    def process_turn(self, card: BaseCard) -> None:
        """Обрабатываем текущий ход."""
        logger.info("Playing card {}", card)
        self.deck.put_on_top(card)
        self.deck.top(self)
        if not self.choose_color_flag:
            self.next_turn()

    def choose_color(self, color: CardColor):
        """Устанавливаем цвет для последней карты."""
        self.deck.top.color = color
        self.next_turn()

    def next_turn(self) -> None:
        """Передаёт ход следующему игроку."""
        logger.info("Next Player")
        self.choose_color_flag = False
        self.turn_start = datetime.now()
        self.skip_players()

    def skip_players(self, n: int = 1) -> None:
        """Пропустить ход для следующих игроков.

        В зависимости от направления игры пропускает несколько игроков.

        Args:
            n (int): Сколько игроков пропустить (1).
        """
        if self.reverse:
            self.current_player = (self.current_player - n) % len(self.players)
        else:
            self.current_player = (self.current_player + n) % len(self.players)
