"""Описывает все карточки Uno и как они используются.

Существует несколько типов карт:
- Числа.
- Пропуск хода.
- Переворот.
- Добавить карты.
- Выбор цвета.
- Дать 4 карты.
"""

from enum import IntEnum
from random import randint
from typing import Any, Iterable, Iterator, Self

from loguru import logger

# Дополнительные перечисления
# ===========================

# Emoji для представления цвета карты
COLOR_EMOJI = ["❤️", "💛", "💚", "💙", "🖤"]

class CardColor(IntEnum):
    """Все доступные цвета карт UNO."""

    RED = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3
    BLACK = 4

    def __str__(self) -> str:
        """Представление цвета в виде смайлика."""
        return COLOR_EMOJI[self.value]

CARD_TYPES = ["", "skip", "reverse", "+", "choose", "take"]

class CardType(IntEnum):
    """Основные типы карт UNO.

    - NUMBER: Числа от 0 до 9.
    - TURN: Пропуск хода следующего игрока.
    - REVERSE: Переворачивает очередь ходов.
    - TAKE: Следующий игрок берёт карты.
    - CHOOSE_COLOR: Выбирает любой цвет для карты.
    - TAKE_FOUR: Выбирает цвет, даёт +4 карты следующему игроку.
    """

    NUMBER = 0
    TURN = 1
    REVERSE = 2
    TAKE = 3
    CHOOSE_COLOR = 4
    TAKE_FOUR = 5

    def __str__(self) -> str:
        """Представление тип карты одним словом."""
        return CARD_TYPES[self.value]


# Описание карт
# =============

class BaseCard:
    """Описание каждой карты Uno.

    Предоставляет общий функционал для всех карт.
    """

    def __init__(self, color: CardColor, card_type: CardType):
        self.color: CardColor = color
        self.card_type: CardType = card_type
        self.value: int = 0
        self.cost: int = 0

    def can_cover(self, other_card: Self) -> bool:
        """Проверяет что другая карта может покрыть текущую.

        По правилам игры цель каждого игрока - избавить от своих карт.
        Чтобы избавиться от карт, нужно накрыть текущую карту с
        верхушки одной из своей руки.
        Как только карты кончатся - вы победили.

        Данный метод проверяет что вы можете покрыть текущую карту
        другой картой.

        Args:
            other_card (BaseCard): Карта, которой вы хотите покрыть
                текущую.

        Returns:
            bool: Можно ли покрыть текущую карту данной

        """
        if other_card.color == CardColor.BLACK:
            return True
        elif self.color == other_card.color:
            return True
        elif (self.card_type == other_card.card_type
            and self.value == other_card.value
        ):
            return True
        return False

    def get_cover_cards(
        self, hand: Iterable[Self]
    ) -> Iterator[tuple[Self, bool]]:
        """Проверяет какие карты вы можете покрыть из своей руки.

        Используется чтобы проверить всю свою руку на наличие карт,
        которыми можно покрыть текущую.

        Args:
            hand (Iterable[BaseCard]): Карты в вашей руке.

        Yields:
            Iterator[BaseCard, bool]: Возвращает карту и можете ли вы
                ею покрыть текущую.

        """
        for card in hand:
            yield (card, self.can_cover(card))

    def use_card(self, game) -> Any:
        """Выполняет способность карты.

        У каждой карты есть свой способность.
        Все способности реализуются путём изменения параметров игры.

        Args:
            game (UnoGame): Текущая игровая сессия где вызвана карта.

        Returns:
            Any: Результат работы карты, возвращаемый обратно в игру.

        """
        logger.debug("Used card {} in chat {}", self, game.chat_id)


    def __call__(self, game) -> None:
        """Синтаксический сахар для вызова действия карты.

        Позволяет использовать способность этой карты.
        Является сокращением для метода use_card.
        """
        return self.use_card(game)

    def __str__(self) -> str:
        """Представление карты в строковом виде."""
        return f"{self.color} {self.card_type} {self.value}"

    def __repr__(self) -> str:
        """Представление карты при отладке."""
        return self.__str__()

    def __eq__(self, other_card: Self) -> bool:
        """Проверяет соответствие двух карт."""
        return (
            self.color == other_card.color
            and self.card_type == other_card.card_type
            and self.value == other_card.value
            and self.cost == other_card.cost
        )

    def __lt__(self, other_card: Self) -> bool:
        """Проверяет что данная карта меньшей стоимости чем прочая."""
        return (
            self.color < other_card.color
            and self.value < other_card.value
            and self.cost < other_card.cost
        )


class NumberCard(BaseCard):
    """Карта с числом.

    Данная карта не обладает какими-либо особенностями.
    Просто карта с определённым число от 0 до 9.
    """

    def __init__(self, color: CardColor, value: int):
        super().__init__(color, CardType.NUMBER)
        self.value = value
        self.cost = value

    def __str__(self) -> str:
        """Представление карты в строковом виде."""
        return f"{self.color} {self.value}"


class TurnCard(BaseCard):
    """Карта пропуска хода.

    Позволяет пропустить ход для следующих игроков.
    """

    def __init__(self, color: CardColor, value: int):
        super().__init__(color, CardType.TURN)
        self.value = value
        self.cost = 20

    def use_card(self, game) -> None:
        """Пропускает ход для следующего игрока.

        Args:
            game (UnoGame): Текущая сессия игры.

        """
        logger.info("Skip {} players", self.value)
        game.skip_players(self.value)

    def __str__(self):
        """Представление карты в строковое виде."""
        return f"{self.color} skip {self.value if self.value != 1 else ''}"


class ReverseCard(BaseCard):
    """Карта разворота.

    Разворачивает очередь ходов.
    """

    def __init__(self, color: CardColor):
        super().__init__(color, CardType.REVERSE)
        self.cost = 20

    def use_card(self, game) -> None:
        """Разворачивает очерёдность ходов для игры.

        Args:
            game (UnoGame): Текущая сессия игры.

        """
        # Когда игроков двое, работает как карта пропуска
        if len(game.players) == 2: # noqa
            game.skip_players()
        else:
            game.reverse = not game.reverse
            logger.info("Reverse flag now {}", game.reverse)

    def __str__(self):
        """Представление карты в строковое виде."""
        return f"{self.color} reverse"


class TakeCard(BaseCard):
    """Взять две карты.

    На самом деле тут может быть и больше.
    Следующий игрок должен будет взять несколько карт.
    """

    def __init__(self, color: CardColor, value: int = 2):
        super().__init__(color, CardType.TAKE)
        self.value = value
        self.cost = 20

    def use_card(self, game):
        """Следующий игрок берёт несколько карт.

        Args:
            game (UnoGame): Текущая сессия игры.

        """
        game.take_counter += self.value
        logger.info("Take counter increase by {} and now {}",
            self.value, game.take_counter
        )

    def __str__(self):
        """Представление карты в строковое виде."""
        return f"{self.color} +{self.value}"


class ChooseColorCard(BaseCard):
    """карта выбора цвета.

    Позволяет изменить цвет текущей карты.
    """

    def __init__(self):
        super().__init__(CardColor.BLACK, CardType.CHOOSE_COLOR)
        self.cost = 50

    def use_card(self, game):
        """Следующий игрок берёт несколько карт.

        Args:
            game (UnoGame): Текущая сессия игры.

        """
        if game.rules.auto_choose_color:
            logger.info("Auto choose color for card")
            if game.reverse:
                self.color = CardColor((game.deck.top.color + 1) % 3)
            else:
                self.color = CardColor((game.deck.top.color - 1) % 3)
        elif game.rules.choose_random_color:
            logger.info("Choose random color for card")
            self.color = CardColor(randint(0, 3))
        else:
            logger.info("Set choose color flag to True")
            game.choose_color_flag = True

    def __str__(self):
        """Представление карты в строковое виде."""
        return f"{self.card_type} {self.color}"


class TakeFourCard(BaseCard):
    """Карта дать +4.

    Особая карта, меняющая цвет и выдающая следующему игроку 4 карты.
    """

    def __init__(self, value: int = 4):
        super().__init__(CardColor.BLACK, CardType.TAKE_FOUR)
        self.value = value
        self.cost = 50

    def use_card(self, game):
        """Следующий игрок берёт несколько карт.

        Args:
            game (UnoGame): Текущая сессия игры.

        """
        if game.rules.auto_choose_color:
            logger.info("Auto choose color for card")
            if game.reverse:
                self.color = CardColor((game.deck.top.color + 1) % 3)
            else:
                self.color = CardColor((game.deck.top.color - 1) % 3)
        elif game.rules.choose_random_color:
            logger.info("Choose random color for card")
            self.color = CardColor(randint(0, 3))
        else:
            game.choose_color_flag = True
        game.take_counter += 4
