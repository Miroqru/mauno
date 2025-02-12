"""Представляет игроков, связанных с текущей игровой сессией."""

from random import randint
from typing import TYPE_CHECKING, NamedTuple, Self

from loguru import logger

from mau.card import (
    BaseCard,
    CardColor,
    NumberCard,
    ReverseCard,
    TakeCard,
    TakeFourCard,
    TurnCard,
)
from mau.enums import GameState
from mau.exceptions import DeckEmptyError

if TYPE_CHECKING:
    from mau.game import UnoGame


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

    def __init__(self, game: "UnoGame", user_id: str, user_name: str) -> None:
        self.hand: BaseCard = []
        self.game: UnoGame = game
        self.user_id = user_id
        self._user_name = user_name

        self.bluffing = False
        self.anti_cheat = 0

        self.shotgun_current = 0
        self.shotgun_lose = 0

    @property
    def name(self) -> str:
        """Возвращает имя игрока с упоминанием пользователя ядл бота."""
        return self._user_name

    @property
    def is_current(self) -> bool:
        """Имеет ли право хода текущий игрок."""
        return self == self.game.player

    # TODO: game.owner.id
    @property
    def is_owner(self) -> bool:
        """Является ли текущий пользователь автором комнаты."""
        return self.user_id == self.game.start_player.id

    def take_first_hand(self) -> None:
        """Берёт начальный набор карт для игры."""
        self.shotgun_lose = randint(1, 8)
        if self.game.rules.debug_cards:
            logger.debug("{} Draw debug first hand for player", self._user_name)
            self.hand = [
                TakeFourCard(),
                TakeFourCard(),
            ]
            for x in (0, 1, 2, 3):
                self.hand.extend(
                    (
                        TakeCard(CardColor(x)),
                        TurnCard(CardColor(x), 1),
                        ReverseCard(CardColor(x)),
                        NumberCard(CardColor(x), 7),
                        NumberCard(CardColor(x), 2),
                        NumberCard(CardColor(x), 0),
                    )
                )
            return

        logger.debug("{} Draw first hand for player", self._user_name)
        try:
            self.hand = list(self.game.deck.take(7))
        except DeckEmptyError:
            for card in self.hand:
                self.game.deck.put(card)
            logger.warning("There not enough cards in deck for player")
            raise DeckEmptyError()

    def take_cards(self) -> None:
        """Игрок берёт заданное количество карт согласно счётчику."""
        take_counter = self.game.take_counter or 1
        logger.debug("{} Draw {} cards", self._user_name, take_counter)

        for card in self.game.deck.take(take_counter):
            self.hand.append(card)
        self.game.take_counter = 0
        self.game.take_flag = True

    def _sort_hand_cards(self, top: BaseCard) -> SortedCards:
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
                self.bluffing or card.color == self.game.deck.top.color
            )

        return SortedCards(sorted(cover), sorted(uncover))

    def _get_equal_cards(self, top: BaseCard) -> SortedCards:
        cover = []
        uncover = []
        for card in self.hand:
            if card != top:
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
                self.bluffing or card.color == self.game.deck.top.color
            )

        return SortedCards(sorted(cover), sorted(uncover))

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

        if self.game.rules.intervention and self.game.player != self:
            return self._get_equal_cards(top)
        return self._sort_hand_cards(top)

    # Обработка событий
    # =================

    def on_leave(self) -> None:
        """Действия игрока при выходе из игры."""
        logger.debug("{} Leave from game", self._user_name)
        # Если он последний игрок, подчищать за собой не приходится
        if len(self.game.players) == 1:
            return

        for card in self.hand:
            self.game.deck.put(card)
        self.hand.clear()

    def twist_hand(self, other_player: Self) -> None:
        """Меняет местами руки для двух игроков."""
        logger.info("Switch hand between {} and {}", self, other_player)
        player_hand = self.hand.copy()
        self.hand = other_player.hand.copy()
        other_player.hand = player_hand
        self.game.next_turn()

    def shotgun(self) -> bool:
        """Выстрелить из револьвера."""
        if self.game.rules.single_shotgun:
            self.game.shotgun_current += 1
            is_fired = self.game.shotgun_current >= self.game.shotgun_lose
            if is_fired:
                self.game.shotgun_lose = randint(1, 8)
                self.game.shotgun_current = 0
            return is_fired
        self.shotgun_current += 1
        return self.shotgun_current >= self.shotgun_lose

    # Обработка игровых действий
    # ==========================

    async def call_bluff(self) -> None:
        """Проверка предыдущего игрока на блеф.

        По правилам, если прошлый игрок блефовал, то он берёт 4 карты.
        Если же игрок не блефовал, текущий игрок берёт уже 6 карт.
        """
        logger.info("{} call bluff {}", self, self.game.prev)
        bluff_player = self.game.bluff_player
        if bluff_player.bluffing:
            self.game.journal.add(
                "🔎 <b>Замечен блеф</b>!\n"
                f"{bluff_player.user.first_name} получает "
                f"{self.game.take_counter} карт."
            )
            bluff_player.take_cards()

            if len(self.game.deck.cards) == 0:
                self.game.journal.add("🃏 В колоде не осталось свободных карт.")
        else:
            self.game.take_counter += 2
            self.game.journal.add(
                f"🎩 {bluff_player.user.first_name} <b>Честный игрок</b>!\n"
                f"{self.name} получает "
                f"{self.game.take_counter} карт.\n"
            )
            self.take_cards()
            if len(self.game.deck.cards) == 0:
                self.game.journal.add("🃏 В колоде не осталось свободных карт.")

        # Завершаем текущий ход
        await self.game.journal.send_journal()
        self.game.next_turn()

    # Магические методы
    # =================

    def __repr__(self) -> str:
        """Представление игрока при отладке."""
        return repr(self._user_name)

    def __str__(self) -> str:
        """Представление игрока в строковом виде."""
        return str(self._user_name)

    def __eq__(self, other_player: Self) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        return self.user_id == other_player.user_id

    def __ne__(self, other_player: Self) -> bool:
        """Проверяет что игроки не совпадают."""
        return self.user_id != other_player.user_id
