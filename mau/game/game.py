"""Игровая сессия."""

from random import choice
from typing import Any

from loguru import logger

from mau.deck.card import CardColor, MauCard
from mau.deck.deck import Deck
from mau.enums import GameState
from mau.events import Event, EventHandler, GameEvents
from mau.game.player import BaseUser, Player
from mau.game.player_manager import GameReverse, PlayerManager
from mau.game.shotgun import Shotgun
from mau.game.timer import GameTimer
from mau.rules import GameRules, RuleSet

_MIN_SHOTGUN_TAKE_COUNTER = 3


class MauGame:
    """Представляет каждую игру Mau.

    Каждая отдельная игра привязывается к конкретному чату.
    Предоставляет методы для обработки карт и очерёдности ходов.
    """

    def __init__(
        self,
        player_manager: PlayerManager,
        event_handler: EventHandler,
        room_id: str,
        owner: BaseUser,
    ) -> None:
        self.room_id = room_id
        self.rules = RuleSet()
        self.pm = player_manager
        self.deck = Deck()
        self.event_handler: EventHandler = event_handler

        self._owner_id = owner.id
        self.pm.add(Player(self, owner.id, owner.name, owner.username))

        self.bluff_state: tuple[str, bool] | None = None
        self.started: bool = False
        self.open: bool = True
        self.take_counter: int = 0
        self.state: GameState = GameState.NEXT
        self.shotgun = Shotgun()
        self.timer = GameTimer()

    @property
    def player(self) -> Player:
        """Возвращает текущего игрока."""
        return self.pm.cur()

    @property
    def owner(self) -> Player:
        """Возвращает владельца игры."""
        return self.pm.get(self._owner_id)

    def is_owner(self, player: Player) -> bool:
        """Проверяет что игрок является владельцем комнаты."""
        return player.user_id == self._owner_id

    def can_play(self, user_id: str) -> bool:
        """Может ли текущий игрок совершать действия."""
        player = self.pm.get_or_none(user_id)
        if player is None:
            return False

        return self.player == player or self.rules.status(
            GameRules.intervention
        )

    def can_cover(self, player: Player, card: MauCard) -> bool:
        """Проверяет может ли текущая карта покрыть верхнюю из колоды."""
        top = self.deck.top

        if (
            self.rules.status(GameRules.intervention)
            and card != top
            and player != self.player
        ):
            return False

        # Для режима побочного выброса
        if (
            self.state == GameState.CONTINUE
            and self.rules.status(GameRules.side_effect)
            and card.cost == top.cost
        ):
            return True

        # Совмещение нескольких карт
        return (
            (top.behavior.on_counter and self.take_counter > 0)
            and not top.behavior.on_counter
            and not self.rules.status(GameRules.deferred_take)
        )

    # TODO: User ID instead Player
    def dispatch(
        self, from_player: Player, event_type: GameEvents, data: Any = None
    ) -> None:
        """Обёртка над методом вызова события.

        Автоматически подставляет текущую игру в событие.
        Вы также можете вызвать событие от имени игрока.
        """
        self.event_handler.dispatch(Event(self, from_player, event_type, data))

    # TODO: Немного не понятно
    def take_cards(self) -> None:
        """Взятие карт игроков.

        Используется когда игрок хочет взять карты.
        """
        if (
            self.rules.status(GameRules.take_until_cover)
            and self.take_counter == 0
        ):
            self.take_counter = self.deck.count_until_cover()

        if (
            self.take_counter > _MIN_SHOTGUN_TAKE_COUNTER
            and (self.rules.status(GameRules.shotgun))
            and self.state != GameState.SHOTGUN
        ):
            self.set_state(GameState.SHOTGUN)

    # управление игрой
    # ================

    def start(self, deck: Deck) -> None:
        """Начинает новую игру в чате."""
        logger.info("Start new game in chat {}", self.room_id)
        self.deck = deck
        self.deck.shuffle()

        wild_color = (
            choice(self.deck.colors)
            if self.rules.status(GameRules.special_wild)
            else CardColor.BLACK
        )
        self.deck.set_wild(wild_color)

        self.pm.start()
        self.timer.start()
        self.started = True
        self.dispatch(self.owner, GameEvents.GAME_START)
        self.deck.top(self)

    def end(self) -> None:
        """Завершает текущую игру."""
        self.pm.end()
        self.started = False
        self.dispatch(self.owner, GameEvents.GAME_END)

    def join_player(self, user: BaseUser) -> Player | None:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", user, self.room_id)
        player = self.pm.get_or_none(user.id)
        if player is not None:
            return player

        if not self.open:
            return None

        player = Player(self, user.id, user.name, user.username)
        self.pm.add(player)
        self.dispatch(player, GameEvents.GAME_JOIN)
        if self.started:
            player.on_join()
        return player

    def leave_player(self, player: Player) -> None:
        """Удаляет пользователя из игры."""
        logger.info("Leaving {} game with id {}", player, self.room_id)
        if not self.started:
            self.pm.remove(player.user_id)
            return

        self.dispatch(player, GameEvents.GAME_LEAVE, player.hand)
        if len(player.hand) == 0:
            self.pm.add_winner(player.user_id)
            if self.rules.status(GameRules.one_winner):
                self.end()
                return
        else:
            self.pm.add_loser(player.user_id)
            if player == self.player:
                self.take_counter = 0

        self.pm.player_cost[player.user_id] = player.count_cost()
        player.on_leave()
        if len(self.pm) <= 1:
            self.end()
        elif self.is_owner(player):
            self._owner_id = self.pm.cur(1).user_id

    # управление состоянием игры
    # ==========================

    def shot(self) -> bool:
        """Выстрелить из револьвера."""
        if not self.rules.status(GameRules.shotgun):
            return False

        res = self.shotgun.shot()
        if res:
            self.shotgun = Shotgun()
        return res

    def set_state(self, state: GameState) -> None:
        """Устанавливает новое состояние для игры."""
        self.state = state
        self.dispatch(self.player, GameEvents.GAME_STATE, state)

    def set_reverse(self, reverse: GameReverse | None = None) -> None:
        """Устанавливает порядок ходов."""
        if reverse is None:
            self.pm.toggle_reverse()
        else:
            self.pm.set_reverse(reverse)
        self.player.dispatch(GameEvents.GAME_REVERSE, self.pm.reverse)

    # Обработка ходов
    # ===============

    def process_turn(self, player: Player, card_index: int) -> None:
        """Обрабатываем текущий ход.

        Сначала применяется действие карты.
        А уже после она ложится на верх колоды.
        """
        card = player.hand.pop(card_index)
        logger.info("Playing card {}", card)
        card(self)

        self.deck.top.on_cover(self)
        self.deck.put_top(card)
        self.dispatch(player, GameEvents.PLAYER_PUT, card)

        if self.state == GameState.NEXT and self.rules.status(
            GameRules.side_effect
        ):
            self.state = GameState.CONTINUE
            return

        if self.state not in (GameState.NEXT, GameState.TAKE):
            return

        if self.rules.status(GameRules.random_color):
            self.choose_color(choice(self.deck.colors))
        else:
            self.player.end_turn()

    def next_turn(self) -> None:
        """Передаёт ход следующему игроку."""
        if not self.started:
            logger.info("Game ended -> stop process turn")
            return

        logger.info("Next Player!")
        # Shotgun надо сбрасывать вручную
        if self.state != GameState.SHOTGUN:
            self.state = GameState.NEXT
        stat = self.timer.tick()
        self.pm.next()
        self.dispatch(self.player, GameEvents.GAME_TURN, stat)
