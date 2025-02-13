"""Игровая сессия.

Представляет класс игровой сессии.
Иначе говоря игровой движок, обрабатывающий ходы игроков и
действия карт из колоды.
"""

from dataclasses import dataclass
from datetime import datetime
from random import randint, shuffle

from loguru import logger

from mau.card import CardColor
from mau.deck import Deck
from mau.enums import GameState
from mau.exceptions import (
    AlreadyJoinedError,
    LobbyClosedError,
    NoGameInChatError,
)
from mau.player import BaseUser, Player
from mau.telegram.journal import BaseJournal


# TODO: Давайте заменим вот этот бред на что-то нормальное
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
    single_shotgun: bool = False
    ahead_of_curve: bool = False
    side_effect: bool = False
    intervention: bool = False


@dataclass(frozen=True, slots=True)
class Rule:
    """Правило для игры."""

    key: str
    name: str


RULES = (
    Rule("twist_hand", "🤝 Обмен руками"),
    Rule("rotate_cards", "🧭 Обмен телами."),
    Rule("take_until_cover", "🍷 Беру до последнего."),
    Rule("single_shotgun", "🎲 Общий револьвер."),
    Rule("shotgun", "🔫 Рулетка."),
    Rule("wild", "🐉 Дикие карты"),
    Rule("auto_choose_color", "🃏 самоцвет"),
    Rule("choose_random_color", "🎨 Случайный цвет"),
    Rule("random_color", "🎨 Какой цвет дальше?"),
    Rule("debug_cards", "🦝 Отладочные карты!"),
    Rule("side_effect", "🌀 Побочный выброс"),
    Rule("ahead_of_curve", "🔪 На опережение 🔧"),
    Rule("intervention", "😈 Вмешательство 🔧"),
)


class UnoGame:
    """Представляет каждую игру Uno.

    Каждая отдельная игра привязывается к конкретному чату.
    Предоставляет методы для обработки карт и очерёдности ходов.
    """

    def __init__(self, journal: BaseJournal, chat_id: int) -> None:
        self.chat_id = chat_id
        self.rules = GameRules()
        self.deck = Deck()
        self.journal: BaseJournal = journal

        # Игроки Uno
        self.current_player: int = 0
        # TODO: Переименовать start player в owner
        # TODO: Изменить на экземпляр игрока, на будущее
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
        self.take_flag: bool = False
        self.state: GameState = GameState.NEXT

        self.shotgun_lose: int = 0
        self.shotgun_current: int = 0

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
            if player.user_id == user_id:
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

        if self.rules.single_shotgun:
            self.shotgun_lose = randint(1, 8)

        for player in self.players:
            player.take_first_hand()

        self.take_first_card()

    def end(self) -> None:
        """Завершает текущую игру."""
        self.players.clear()
        self.started = False

    def take_first_card(self) -> None:
        """Берёт первую карту для начали игры."""
        while self.deck.top is None or self.deck.top.color == CardColor.BLACK:
            card = self.deck.take_one()
            if card.color == CardColor.BLACK:
                self.deck.put(card)
            else:
                self.deck.put_on_top(card)

        self.deck.top(self)

    def choose_color(self, color: CardColor) -> None:
        """Устанавливаем цвет для последней карты."""
        self.deck.top.color = color
        self.next_turn()

    def next_turn(self) -> None:
        """Передаёт ход следующему игроку."""
        logger.info("Next Player")
        self.state = GameState.NEXT
        self.take_flag = False
        self.turn_start = datetime.now()
        self.journal.clear()
        self.skip_players()

    # Управление списком игроков
    # ==========================

    def add_player(self, user: BaseUser) -> None:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", user, self.chat_id)
        if not self.open:
            raise LobbyClosedError()

        player = self.get_player(user.id)
        if player is not None:
            raise AlreadyJoinedError()

        player = Player(self, user.id, user.mention_html())
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
            # Скорее всего игрок застрелился, больше карты не берём
            self.take_counter = 0
            self.next_turn()

        if len(player.hand) == 0:
            self.winners.append(player)
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

    def rotate_cards(self) -> None:
        """Меняет карты в руках для всех игроков."""
        last_hand = self.players[-1].hand.copy()
        for i in range(len(self.players) - 1, 0, -1):
            self.players[i].hand = self.players[i - 1].hand.copy()

        self.players[0].hand = last_hand

    def set_current_player(self, player: Player) -> None:
        """Устанавливает курсор текущего игрока на переданного."""
        for i, pl in enumerate(self.players):
            if player == pl:
                self.current_player = i
                return
