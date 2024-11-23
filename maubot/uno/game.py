"""Игровая сессия.

Представляет класс игровой сессии.
Иначе говоря игровой движок, обрабатывающий ходы игроков и
действия карт из колоды.
"""

from dataclasses import dataclass
from datetime import datetime
from random import randint, shuffle

from loguru import logger

from maubot.uno.card import BaseCard, CardColor
from maubot.uno.deck import Deck
from maubot.uno.enums import GameState
from maubot.uno.exceptions import (
    AlreadyJoinedError,
    LobbyClosedError,
    NoGameInChatError,
)
from maubot.uno.player import Player


@dataclass(slots=True)
class GameRules:
    """Набор игровых правил, которые можно менять при запуске игры."""

    wild: bool = False
    auto_choose_color: bool = False
    choose_random_color: bool = False
    random_color: bool = False
    debug_cards: bool = False
    twist_hand: bool = False
    rotate_cards: bool = False
    take_until_cover: bool = False
    shotgun: bool = False

@dataclass(frozen=True, slots=True)
class Rule:
    """Правило для игры."""

    key: str
    name: str

RULES = (
    Rule("wild", "🐉 Дикие карты"),
    Rule("auto_choose_color", "🃏 самоцвет"),
    Rule("choose_random_color", "🎨 Случайный цвет"),
    Rule("random_color", "🎨 Какой цвет дальше?"),
    Rule("debug_cards", "🦝 Отладочные карты!"),
    Rule("twist_hand", "🤝 Обмен руками"),
    Rule("rotate_cards", "🧭 Обмен телами."),
    Rule("take_until_cover", "🍷 Беру до последнего."),
    Rule("shotgun", "🔫 Рулетка."),
)


class UnoGame:
    """Представляет каждую игру Uno.

    Каждая отдельная игра привязывается к конкретному чату.
    Предоставляет методы для обработки карт и очерёдности ходов.
    """

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.rules = GameRules()
        self.deck = Deck()

        # Игроки Uno
        self.current_player: int = 0
        self.start_player = None
        self.bluff_player: Player = None
        self.players: list[Player] = []
        self.winners: list[Player] = []
        self.losers: list[Player] = []

        # Настройки игры
        self.started: bool = False
        self.open: bool = True
        self.reverse: bool = False
        self.take_counter: int = 0
        self.state: GameState = GameState.NEXT

        # Таймеры
        self.game_start = datetime.now()
        self.turn_start = datetime.now()

    @property
    def player(self) -> Player:
        """Возвращает текущего игрока."""
        return self.players[self.current_player % len(self.players)]

    @property
    def prev(self) -> Player:
        """Возвращает предыдущего игрока."""
        if self.reverse:
            prev_index = (self.current_player + 1) % len(self.players)
        else:
            prev_index = (self.current_player - 1) % len(self.players)
        return self.players[prev_index]


    def get_player(self, user_id: int) -> Player | None:
        """Получает игрока среди списка игроков по его ID."""
        for player in self.players:
            if player.user.id == user_id:
                return player
        return None


    # Управление потоком игры
    # =======================

    def start(self) -> None:
        """Начинает новую игру в чате."""
        logger.info("Start new game in chat {}", self.chat_id)
        self.winners.clear()
        self.losers.clear()
        self.started = True
        shuffle(self.players)

        if self.rules.wild:
            self.deck.fill_wild()
        else:
            self.deck.fill_classic()

        for player in self.players:
            player.take_first_hand()

        self.take_first_card()

    def end(self) -> None:
        """Завершает текущую игру."""
        self.players.clear()
        self.started = False

    def take_first_card(self):
        """Берёт первую карту для начали игры."""
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
        card(self)
        self.deck.put_on_top(card)
       
        if (self.rules.twist_hand
            and self.deck.top.cost == 2
            and len(self.player.hand) > 1
        ):
            self.state = GameState.TWIST_HAND
        elif self.state == GameState.NEXT:
            if self.rules.random_color:
                self.deck.top.color = CardColor(randint(0, 3))
            elif (self.rules.rotate_cards
                and self.deck.top.cost == 0
                and len(self.player.hand) > 1
            ):
                self.rotate_cards()       
            self.next_turn()

    def choose_color(self, color: CardColor):
        """Устанавливаем цвет для последней карты."""
        self.deck.top.color = color
        self.next_turn()

    def next_turn(self) -> None:
        """Передаёт ход следующему игроку."""
        logger.info("Next Player")
        self.state = GameState.NEXT
        self.player.took_card = False
        self.turn_start = datetime.now()
        self.skip_players()


    # Управление списком игроков
    # ==========================

    def add_player(self, user) -> None:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", user, self.chat_id)
        if not self.open:
            raise LobbyClosedError()

        player = self.get_player(user.id)
        if player is not None:
            raise AlreadyJoinedError()

        player = Player(self, user)
        player.on_leave()
        if self.started:
            player.take_first_hand()

        self.players.append(player)

    def remove_player(self, user_id: int) -> None:
        """Удаляет пользователя из игры."""
        logger.info("Leaving {} game with id {}", user_id, self.chat_id)

        player = self.get_player(user_id)
        if player is None:
            raise NoGameInChatError()

        if player == self.player:
            self.next_turn()
            if self.state == GameState.SHOTGUN:
                self.losers.append(player)
        else:
            self.losers.append(player)

        player.on_leave()
        self.players.remove(player)

        if len(self.players) <= 1:
            self.winners.extend(self.players)
            self.end()

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

    def rotate_cards(self):
        """Меняет карты в руках для всех игроков."""
        last_hand = self.players[-1].hand.copy()
        for i in range(len(self.players) - 1, 0, -1):
            self.players[i].hand = self.players[i - 1].hand.copy()

        self.players[0].hand = last_hand
