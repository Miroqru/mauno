"""Игровая сессия."""

from random import choice

from loguru import logger

from mau.deck.card import MauCard
from mau.deck.deck import Deck
from mau.enums import GameState
from mau.events import EventHandler, EventType
from mau.game.player import Player, PlayerID, PlayerOrID
from mau.game.player_manager import GameReverse, PlayerManager, ResultType
from mau.game.settings import GameSettings
from mau.game.shotgun import Shotgun
from mau.game.timer import GameTimer
from mau.rules import GameRules, RuleSet
from mau.session import RoomID

_MIN_SHOTGUN_TAKE_COUNTER = 3


class MauGame:
    """Представляет каждую игру Mau.

    Каждая отдельная игра привязывается к конкретному чату.
    Предоставляет методы для обработки карт и очерёдности ходов.
    """

    def __init__(self, settings: GameSettings, handler: EventHandler) -> None:
        self._settings = settings
        self.event_handler: EventHandler = handler

        # TOOD: Метод смены владельца
        self.pm = PlayerManager(settings.min_players, settings.max_players)
        self.pm.add(Player(self, settings.owner_id, settings.owner_name))

        # Игровые компоненты
        self.deck = Deck()
        self.shotgun = Shotgun()
        self.timer = GameTimer()

        self.bluff_state: tuple[str, bool] | None = None
        self.started: bool = False
        self.take_counter: int = 0
        self.state: GameState = GameState.NEXT

    @property
    def settings(self) -> GameSettings:
        """Возвращает настройки для текущей комнаты."""
        return self._settings

    @property
    def rules(self) -> RuleSet:
        """Игровые правила для сессии.

        Сокращение для game.settings.rules.
        Сделано для обратной совместимости с прошлыми версиями.
        Правила изменяются также через это свойство.
        """
        return self.settings.rules

    @property
    def room_id(self) -> RoomID:
        """Возвращает привязанную к комнате игру.

        Сокращение для game.settings.rules.
        Сделано для обратной совместимости с прошлыми версиями.
        """
        return self.settings.room_id

    # TODO: Оповещать об изменениях в настройках
    def update_settings(self, settings: GameSettings) -> None:
        """Применяет новые настройки для комнаты."""
        if self._settings.max_players != settings.max_players:
            self.pm.max_players = settings.max_players

        if self._settings.min_players != settings.min_players:
            self.pm.min_players = settings.min_players

        self._settings = settings

    @property
    def player(self) -> Player:
        """Возвращает текущего игрока.

        Alias для `pm.cur()` с нулевым сдвигом.
        """
        return self.pm.cur()

    @property
    def owner(self) -> Player:
        """Возвращает владельца текущей игры."""
        return self.pm.get(self._owner_id)

    def is_owner(self, player: Player) -> bool:
        """Проверяет что игрок является владельцем комнаты."""
        return player.id == self._owner_id

    def can_play(self, player: PlayerOrID) -> bool:
        """Может ли текущий игрок совершать действия."""
        if not isinstance(player, Player):
            pl = self.pm.get_or_none(player)
            if pl is None:
                return False
            player = pl

        return self.player == player or self.rules.status(GameRules.intervention)

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

    def take_cards(self) -> None:
        """Взятие карт игроков.

        Используется когда игрок хочет взять карты.
        """
        if self.rules.status(GameRules.take_until_cover) and self.take_counter == 0:
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

        if self.rules.status(GameRules.special_wild):
            self.deck.set_wild(choice(self.deck.colors))

        self.pm.start()
        self.timer.start()
        self.started = True
        self.owner.dispatch(EventType.GAME_START, None)
        self.deck.top(self)

    def end(self) -> None:
        """Завершает текущую игру."""
        self.pm.end()
        self.started = False
        self.owner.dispatch(EventType.GAME_END, None)

    def join_player(self, player_id: PlayerID, name: str) -> Player | None:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", name, self.room_id)
        player = self.pm.get_or_none(player_id)
        if player is not None:
            return player

        if not self.settings.open:
            return None

        player = Player(self, player_id, name)
        self.pm.add(player)
        player.dispatch(EventType.GAME_JOIN, None)
        if self.started:
            player.on_join()
        return player

    def leave_player(self, player: Player) -> None:
        """Удаляет пользователя из игры."""
        logger.info("Leaving {} game with id {}", player, self.room_id)
        if not self.started:
            self.pm.remove(player.id)
            return

        # В будущем может быть больше вариантов победы
        result = ResultType.WINNER if len(player.hand) == 0 else ResultType.LOOSER

        player.dispatch(EventType.GAME_LEAVE, result)
        self.pm.leave(player, result)

        if result == ResultType.WINNER and self.rules.status(GameRules.one_winner):
            self.end()
            return

        if player == self.player:
            self.take_counter = 0

        player.on_leave()

        if len(self.pm) <= 1:
            self.end()
            return

        # TODO: Почему это выглядит как костыль
        if self.is_owner(player):
            self._owner_id = self.pm.cur(1).id

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
        self.player.dispatch(EventType.GAME_STATE, state)

    def set_reverse(self, reverse: GameReverse | None = None) -> None:
        """Устанавливает порядок ходов."""
        self.pm.set_reverse(reverse)
        self.player.dispatch(EventType.GAME_REVERSE, self.pm.reverse)

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
        player.dispatch(EventType.PLAYER_PUT, card)

        if self.state == GameState.NEXT and self.rules.status(GameRules.side_effect):
            self.state = GameState.CONTINUE
            return

        if self.state not in (GameState.NEXT, GameState.TAKE):
            return

        if self.rules.status(GameRules.random_color):
            player.choose_color(choice(self.deck.colors))
        else:
            player.end_turn()

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
        self.player.dispatch(EventType.GAME_TURN, stat)
