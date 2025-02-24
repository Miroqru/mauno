"""Игровая сессия.

Представляет класс игровой сессии.
Иначе говоря игровой движок, обрабатывающий ходы игроков и
действия карт из колоды.
"""

from dataclasses import dataclass
from datetime import datetime
from random import randint, shuffle
from typing import NamedTuple

from loguru import logger

from mau.card import BaseCard, CardColor, CardType
from mau.deck import Deck
from mau.enums import GameState
from mau.exceptions import (
    AlreadyJoinedError,
    LobbyClosedError,
    NoGameInChatError,
)
from mau.journal import BaseJournal, EventAction
from mau.keyboards import select_player_markup
from mau.messages import end_game_message, get_room_players
from mau.player import BaseUser, Player

TWIST_HAND_NUM = 2


@dataclass(slots=True)
class Rule:
    """Правило для игры."""

    name: str
    status: bool
    key: str


# TODO: Давайте заменим вот этот бред на что-то нормальное
class GameRules(NamedTuple):
    """Набор игровых правил, которые можно менять при запуске игры."""

    twist_hand: Rule = Rule("🤝 Обмен руками", False, "twist_hand")
    rotate_cards: Rule = Rule("🧭 Обмен телами.", False, "rotate_cards")
    take_until_cover: Rule = Rule(
        "🍷 Беру до последнего.", False, "take_until_cover"
    )
    single_shotgun: Rule = Rule("🎲 Общий револьвер.", False, "single_shotgun")
    shotgun: Rule = Rule("🔫 Рулетка.", False, "shotgun")
    wild: Rule = Rule("🐉 Дикие карты", False, "wild")
    auto_choose_color: Rule = Rule("🃏 самоцвет", False, "auto_choose_color")
    choose_random_color: Rule = Rule(
        "🎨 Случайный цвет", False, "choose_random_color"
    )
    random_color: Rule = Rule("🎨 Какой цвет дальше?", False, "random_color")
    debug_cards: Rule = Rule("🦝 Отладочные карты!", False, "debug_cards")
    side_effect: Rule = Rule("🌀 Побочный выброс", False, "side_effect")
    ahead_of_curve: Rule = Rule("🔪 На опережение 🔧", False, "ahead_of_curve")
    intervention: Rule = Rule("😈 Вмешательство 🔧", False, "intervention")


class UnoGame:
    """Представляет каждую игру Uno.

    Каждая отдельная игра привязывается к конкретному чату.
    Предоставляет методы для обработки карт и очерёдности ходов.
    """

    def __init__(
        self, journal: BaseJournal, room_id: str, owner: BaseUser
    ) -> None:
        self.room_id = room_id
        self.rules = GameRules()
        self.deck = Deck()
        self.journal: BaseJournal = journal

        # Игроки Uno
        self.current_player: int = 0
        self.owner = Player(self, owner.id, owner.name)
        self.bluff_player: Player | None = None
        self.players: list[Player] = [self.owner]
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

        # TODO: Вот вы не знали, а оно существует
        self.lobby_message: None | int = None

    @property
    def player(self) -> Player:
        """Возвращает текущего игрока."""
        if len(self.players) == 0:
            raise ValueError("Game not started to get players")
        return self.players[self.current_player % len(self.players)]

    @property
    def prev(self) -> Player:
        """Возвращает предыдущего игрока."""
        if self.reverse:
            prev_index = (self.current_player + 1) % len(self.players)
        else:
            prev_index = (self.current_player - 1) % len(self.players)
        return self.players[prev_index]

    def get_player(self, user_id: str) -> Player | None:
        """Получает игрока среди списка игроков по его ID."""
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None

    # Управление потоком игры
    # =======================

    def start(self) -> None:
        """Начинает новую игру в чате."""
        logger.info("Start new game in chat {}", self.room_id)
        self.winners.clear()
        self.losers.clear()
        self.started = True
        shuffle(self.players)

        if self.rules.wild.status:
            self.deck.fill_wild()
        else:
            self.deck.fill_classic()

        if self.rules.single_shotgun.status:
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
        # Это конечно костыль, тем ен менее сейчас это лучшее решение
        while self.deck._top is None or self.deck._top.color == CardColor.BLACK:
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
        logger.info("Next Pltopayer")
        self.state = GameState.NEXT
        self.take_flag = False
        self.turn_start = datetime.now()
        self.journal.clear()
        self.skip_players()

    # Управление списком игроков
    # ==========================

    def add_player(self, user: BaseUser) -> None:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", user, self.room_id)
        if not self.open:
            raise LobbyClosedError()

        player = self.get_player(user.id)
        if player is not None:
            raise AlreadyJoinedError()

        player = Player(self, user.id, user.name)
        player.on_leave()
        if self.started:
            player.take_first_hand()

        self.players.append(player)

    def remove_player(self, user_id: str) -> None:
        """Удаляет пользователя из игры."""
        logger.info("Leaving {} game with id {}", user_id, self.room_id)

        player = self.get_player(user_id)
        if player is None:
            # TODO: Тту должно быть более конкретное исключение
            raise NoGameInChatError

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
            # Если игрок сам вышел/проиграл. другие побеждают
            if player == self.player:
                self.winners.extend(self.players)
            else:
                self.losers.extend(self.players)
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

    async def process_turn(self, card: BaseCard, player: Player) -> None:
        """Обрабатываем текущий ход."""
        logger.info("Playing card {}", card)
        self.deck.put_on_top(card)
        player.hand.remove(card)

        card(self)

        if len(player.hand) == 1:
            self.journal.add("🌟 UNO!\n")

        if len(player.hand) == 0:
            self.journal.add(f"👑 {player.name} победил(а)!\n")
            self.remove_player(player.user_id)
            if not self.started:
                self.journal.add(end_game_message(self))
                self.journal.set_actions(None)

        elif card.cost == TWIST_HAND_NUM and self.rules.twist_hand.status:
            self.journal.add(f"✨ {player.name} Задумывается c кем обменяться.")
            self.state = GameState.TWIST_HAND
            self.journal.set_actions(select_player_markup(self))

        elif self.rules.rotate_cards.status and self.deck.top.cost == 0:
            self.rotate_cards()
            self.journal.add(
                "🤝 Все игроки обменялись картами по кругу.\n"
                f"{get_room_players(self)}"
            )

        if card.card_type in (CardType.TAKE_FOUR, CardType.CHOOSE_COLOR):
            self.journal.add(f"✨ {player.name} Задумывается о выборе цвета.")
            self.state = GameState.CHOOSE_COLOR
            self.journal.set_actions(
                [
                    EventAction(text="❤️", callback_data="color:0"),
                    EventAction(text="💛", callback_data="color:1"),
                    EventAction(text="💚", callback_data="color:2"),
                    EventAction(text="💙", callback_data="color:3"),
                ]
            )

        if any(
            (
                self.rules.random_color.status,
                self.rules.choose_random_color.status,
                self.rules.auto_choose_color.status,
            )
        ):
            self.journal.add(f"🎨 Текущий цвет.. {self.deck.top.color}")

        self.journal.send_journal()

        if self.state == GameState.NEXT and self.started:
            if self.rules.random_color.status:
                self.deck.top.color = CardColor(randint(0, 3))
            if self.deck.top.cost == 1 and self.rules.side_effect.status:
                logger.info("Player continue turn")
            else:
                self.next_turn()
