"""Игровая сессия."""

from datetime import datetime
from random import randint

from loguru import logger

from mau.deck.card import MauCard
from mau.deck.deck import Deck, RandomDeck
from mau.deck.presets import DeckGenerator
from mau.enums import CardColor, GameEvents, GameState
from mau.events import BaseEventHandler, Event
from mau.game.player import BaseUser, Player
from mau.game.player_manager import PlayerManager
from mau.game.rules import GameRules
from mau.game.shotgun import Shotgun


class MauGame:
    """Представляет каждую игру Mau.

    Каждая отдельная игра привязывается к конкретному чату.
    Предоставляет методы для обработки карт и очерёдности ходов.
    """

    def __init__(
        self,
        player_manager: PlayerManager,
        event_handler: BaseEventHandler,
        room_id: str,
        owner: BaseUser,
    ) -> None:
        self.room_id = room_id
        self.rules = GameRules()
        self.deck_generator = DeckGenerator.from_preset("classic")

        self.min_players = 2
        self.max_players = 6
        self.pm = player_manager
        self.deck = Deck()
        self.event_handler: BaseEventHandler = event_handler

        self.owner = Player(self, owner.id, owner.name, owner.username)
        self.pm.add(self.owner)

        # TODO: Может стоит хранить не всего игрока?
        self.bluff_player: tuple[Player, bool] | None = None
        self.started: bool = False
        self.open: bool = True
        self.reverse: bool = False
        self.take_counter: int = 0
        self.state: GameState = GameState.NEXT
        self.shotgun = Shotgun()

        # Таймеры
        self.game_start = datetime.now()
        self.turn_start = datetime.now()

    @property
    def player(self) -> Player:
        """Возвращает текущего игрока."""
        return self.pm.current

    def can_play(self, user_id: str) -> bool:
        """Может ли текущий игрок совершать действия."""
        player = self.pm.get_or_none(user_id)
        if player is None:
            return False

        return self.player == player or self.rules.intervention.status

    def push_event(
        self, from_player: Player, event_type: GameEvents, data: str = ""
    ) -> None:
        """Обёртка над методом journal.push.

        Автоматически подставляет текущую игру.
        """
        self.event_handler.push(Event(self, from_player, event_type, data))

    def start(self) -> None:
        """Начинает новую игру в чате."""
        logger.info("Start new game in chat {}", self.room_id)
        if self.rules.random_cards.status:
            self.deck = RandomDeck()
        else:
            self.deck = self.deck_generator.deck
        self.deck.shuffle()
        self.pm.start()

        if self.rules.single_shotgun.status:
            self.shotgun.reset()

        self.started = True
        self.push_event(self.owner, GameEvents.GAME_START)
        self.deck.top(self)

    def end(self) -> None:
        """Завершает текущую игру."""
        self.pm.end()
        self.started = False
        self.push_event(self.owner, GameEvents.GAME_END)

    def choose_color(self, color: CardColor) -> None:
        """Устанавливаем цвет для последней карты."""
        self.deck.top.color = color
        self.push_event(self.player, GameEvents.GAME_SELECT_COLOR, str(color))
        self.next_turn()

    def next_turn(self) -> None:
        """Передаёт ход следующему игроку."""
        logger.info("Next Player!")
        self.state = GameState.NEXT
        self.turn_start = datetime.now()
        self.pm.next(1, self.reverse)
        logger.warning(self.pm._cp)
        self.push_event(self.player, GameEvents.GAME_TURN)

    def join_player(self, user: BaseUser) -> Player | None:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", user, self.room_id)
        player = self.pm.get_or_none(user.id)
        if player is not None:
            return player

        if not self.open or len(self.pm) >= self.max_players:
            return None

        player = Player(self, user.id, user.name, user.username)
        self.pm.add(player)
        self.push_event(player, GameEvents.GAME_JOIN)
        if self.started:
            player.on_join()
        return player

    def leave_player(self, player: Player) -> None:
        """Удаляет пользователя из игры."""
        logger.info("Leaving {} game with id {}", player, self.room_id)
        if len(player.hand) == 0:
            self.push_event(player, GameEvents.GAME_LEAVE, "win")
            if self.rules.one_winner.status:
                self.end()
        else:
            self.push_event(player, GameEvents.GAME_LEAVE, "lose")
            if player == self.player:
                self.take_counter = 0

        # Если игрок решил закончить чёрной картой
        if self.state == GameState.CHOOSE_COLOR:
            self.choose_color(CardColor(randint(0, 3)))

        self.pm.remove(player)
        if self.started and len(self.pm) <= 1:
            self.end()

    # TODO: Может удалим?
    def skip_players(self, n: int = 1) -> None:
        """Пропустить ход для следующих игроков.

        В зависимости от направления игры пропускает несколько игроков.
        """
        logger.info("Skip {} players", n)
        self.pm.next(n, self.reverse)

    def rotate_cards(self) -> None:
        """Меняет карты в руках для всех игроков."""
        self.pm.rotate_cards(self.reverse)
        self.push_event(self.player, GameEvents.GAME_ROTATE)

    def process_turn(self, card: MauCard, player: Player) -> None:
        """Обрабатываем текущий ход.

        Сначала применяется действие карты.
        А уже после она ложится на верх колоды.
        """
        logger.info("Playing card {}", card)
        card(self)
        # TODO: Как-то смущает меня такой ход
        self.deck.put_top(card, self)
        player.hand.remove(card)
        self.push_event(player, GameEvents.PLAYER_PUSH, card.pack())

        if len(player.hand) == 1:
            self.push_event(player, GameEvents.PLAYER_MAU)

        if len(self.pm.current.hand) == 0:
            self.leave_player(self.pm.current)

        if not self.started:
            logger.info("Game ended -> stop process turn")
            return

        if self.state in (GameState.NEXT, GameState.TAKE):
            # TODO: Вынести в паттерн поведения
            if self.deck.top.cost == 1 and self.rules.side_effect.status:
                logger.info("Player continue turn")
            elif self.rules.random_color.status:
                self.choose_color(CardColor(randint(0, 3)))
            else:
                self.next_turn()

    def set_state(self, state: GameState) -> None:
        """Устанавливает новое состояние для игры."""
        self.state = state
        self.push_event(self.player, GameEvents.GAME_STATE, str(state.value))
