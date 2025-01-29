"""Представляет игроков, связанных с текущей игровой сессией."""

from random import randint
from typing import TYPE_CHECKING, NamedTuple, Self

from aiogram.types import User
from loguru import logger

from maubot import keyboards
from maubot.uno.card import (
    BaseCard,
    CardColor,
    NumberCard,
    ReverseCard,
    TakeCard,
    TakeFourCard,
    TurnCard,
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

    def __init__(self, game: 'UnoGame', user: User) -> None:
        self.hand: BaseCard = []
        self.game: UnoGame = game
        self.user = user

        self.bluffing = False
        self.anti_cheat = 0

        self.shotgun_current = 0
        self.shotgun_lose = 0

    @property
    def name(self) -> str:
        """Возвращает имя игрока с упоминанием пользователя ядл бота."""
        return self.user.mention_html()

    @property
    def is_current(self) -> bool:
        """Имеет ли право хода текущий игрок."""
        return self == self.game.player

    @property
    def is_owner(self) -> bool:
        """Является ли текущий пользователь автором комнаты."""
        return self.user.id == self.game.start_player.id

    def take_first_hand(self) -> None:
        """Берёт начальный набор карт для игры."""
        self.shotgun_lose = randint(1, 8)
        if self.game.rules.debug_cards:
            logger.debug("{} Draw debug first hand for player", self.user)
            self.hand = [
                TakeFourCard(),
                TakeFourCard(),
            ]
            for x in (0, 1, 2, 3):
                self.hand.extend((
                    TakeCard(CardColor(x)),
                    TurnCard(CardColor(x), 1),
                    ReverseCard(CardColor(x)),
                    NumberCard(CardColor(x), 7),
                    NumberCard(CardColor(x), 2),
                    NumberCard(CardColor(x), 0),
                ))
            return

        logger.debug("{} Draw first hand for player", self.user)
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
        logger.debug("{} Draw {} cards", self.user, take_counter)

        for card in self.game.deck.take(take_counter):
            self.hand.append(card)
        self.game.take_counter = 0
        self.game.take_flag = True

    def put_card(self, card_index: int) -> None:
        """Разыгрывает одну из карт из своей руки."""
        card = self.hand.pop(card_index)
        self.game.process_turn(card)

    def _sort_hand_cards(self, top) -> SortedCards:
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

    def _get_equal_cards(self, top) -> SortedCards:
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
                self.bluffing
                or card.color == self.game.deck.top.color
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
        logger.debug("{} Leave from game", self.user)
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
                f"{self.user.first_name} получает "
                f"{self.game.take_counter} карт.\n"
            )
            self.take_cards()
            if len(self.game.deck.cards) == 0:
                self.game.journal.add("🃏 В колоде не осталось свободных карт.")

        # Завершаем текущий ход
        await self.game.journal.send_journal()
        self.game.next_turn()

    async def call_take_cards(self) -> None:
        """Действия игрока при взятии карты.

        В зависимости от правил, можно взять не одну карту, а сразу
        несколько.
        Если включен револьвер, то при взятии нескольких карт будет
        выбор:

        - Брать карты сейчас.
        - Выстрелить, чтобы взял следующий игрок.
        """
        if self.game.rules.take_until_cover and self.game.take_counter == 0:
            self.game.take_counter = self.game.deck.count_until_cover()
            self.game.journal.add(f"🍷 беру {self.game.take_counter} карт.\n")

        if any(self.game.take_counter > 3,
            self.game.rules.shotgun,
            self.game.rules.single_shotgun
        ):
            current = (
                self.game.shotgun_current if self.game.rules.single_shotgun
                else self.shotgun_current
            )
            self.game.journal.add(
                "💼 У нас для Вас есть <b>деловое предложение</b>!\n\n"
                f"Вы можете <b>взять свои карты</b> "
                "или же попробовать <b>выстрелить из револьвера</b>.\n"
                "Если вам повезёт, то карты будет брать уже следующий игрок.\n"
                f"🔫 Из револьвера стреляли {current} / 8 раз\n."
            )
            self.game.journal.set_markup(keyboards.SHOTGUN_REPLY)

        logger.info("{} take cards", self)
        take_counter = self.game.take_counter
        self.take_cards()
        if len(self.game.deck.cards) == 0:
            self.game.journal.add("🃏 В колоде не осталось карт для игрока.")

        # Если пользователь выбрал взять карты, то он пропускает свой ход
        if (isinstance(self.game.deck.top, TakeCard | TakeFourCard)
            and take_counter
        ):
            self.game.next_turn()
        else:
            self.game.state = GameState.NEXT


    # Магические методы
    # =================

    def __repr__(self) -> str:
        """Представление игрока при отладке."""
        return repr(self.user)

    def __str__(self) -> str:
        """Представление игрока в строковом виде."""
        return str(self.user)

    def __eq__(self, other_player: Self) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        return self.user.id == other_player.user.id

    def __ne__(self, other_player: Self) -> bool:
        """Проверяет что игроки не совпадают."""
        return self.user.id != other_player.user.id
