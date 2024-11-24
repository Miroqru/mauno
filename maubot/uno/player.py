"""Представляет игроков, связанных с текущей игровой сессией."""

from random import randint
from typing import TYPE_CHECKING, NamedTuple, Self

from loguru import logger

from maubot.uno.card import (
    BaseCard,
    CardColor,
    NumberCard,
    TakeCard,
    TakeFourCard,
)
from maubot.uno.enums import GameState
from maubot.uno.exceptions import DeckEmptyError

if TYPE_CHECKING:
    from maubot.uno.game import UnoGame


# Дополнительные типы данных
# ==========================

class SortedCards(NamedTuple):
    """Распределяет карты на: покрывающие и не покрывающие."""

    cover: list[BaseCard]
    uncover: list[BaseCard]


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
        self.anti_cheat = 0

        self.shotgun_current = 0
        self.shotgun_lose = 0

    @property
    def is_current(self) -> bool:
        """Имеет ли право хода текущий игрок."""
        return self == self.game.player

    @property
    def is_owner(self) -> bool:
        """Является ли текущий пользователь автором комнаты."""
        return self.user.id == self.game.start_player.id

    def take_first_hand(self):
        """Берёт начальный набор карт для игры."""
        if self.game.rules.debug_cards:
            logger.debug("{} Draw debug first hand for player", self.user)
            self.hand = [
                TakeFourCard(),
                TakeFourCard(),
                TakeCard(CardColor(0)),
                TakeCard(CardColor(1)),
                TakeCard(CardColor(2)),
                TakeCard(CardColor(3)),
                NumberCard(CardColor(0), 7),
                NumberCard(CardColor(1), 7),
                NumberCard(CardColor(2), 7),
                NumberCard(CardColor(3), 7)
            ]
            return

        logger.debug("{} Draw first hand for player", self.user)
        try:
            self.hand = list(self.game.deck.take(7))
        except DeckEmptyError:
            for card in self.hand:
                self.game.deck.put(card)
            logger.warning("There not enough cards in deck for player")
            raise DeckEmptyError()
        self.shotgun_lose = randint(1, 8)

    def take_cards(self):
        """Игрок берёт заданное количество карт согласно счётчику."""
        take_counter = self.game.take_counter or 1
        logger.debug("{} Draw {} cards", self.user, take_counter)

        for card in self.game.deck.take(take_counter):
            self.hand.append(card)
        self.game.take_counter = 0
        self.game.take_flag = True

    def put_card(self, card_index: int):
        """Разыгрывает одну из карт из своей руки."""
        card = self.hand.pop(card_index)
        self.game.process_turn(card)

    def get_cover_cards(self) -> SortedCards:
        """Возвращает отсортированный список карт из руки пользователя.

        Карты делятся на те, которыми он может покрыть и которыми не может
        покрыть текущую верхнюю карту.
        """
        top = self.game.deck.top
        logger.debug("Last card was {}", top)
        self.bluffing = False
        if isinstance(top, TakeFourCard) and self.game.take_counter:
            return SortedCards([], self.hand)
        if self.game.state == GameState.SHOTGUN:
            return SortedCards([], self.hand)

        cover = []
        uncover = []
        for card, can_cover in top.get_cover_cards(self.hand):
            if not can_cover:
                uncover.append(card)
                continue
            if (
                isinstance(top, TakeCard)
                and self.game.take_counter
                and not isinstance(card, TakeCard)
            ):
                uncover.append(card)
                continue

            cover.append(card)
            self.bluffing = (
                self.bluffing
                or card.color == self.game.deck.top.color
            )

        return SortedCards(sorted(cover), sorted(uncover))


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

    def twist_hand(self, other_player: Self) -> None:
        """Меняет местами руки для двух игроков."""
        logger.info("Switch hand between {} and {}", self, other_player)
        player_hand = self.hand.copy()
        self.hand = other_player.hand.copy()
        other_player.hand = player_hand
        self.game.next_turn()

    def shotgun(self) -> bool:
        """Выстрелить из револьвера."""
        self.shotgun_current += 1
        return self.shotgun_current >= self.shotgun_lose


    # Магические методы
    # =================

    def __repr__(self):
        """Представление игрока при отладке."""
        return repr(self.user)

    def __str__(self):
        """Представление игрока в строковом виде."""
        return str(self.user)

    def __eq__(self, other_player: Self) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        return self.user.id == other_player.user.id

    def __ne__(self, other_player: Self) -> bool:
        """Проверяет что игроки не совпадают."""
        return self.user.id != other_player.user.id
