"""Поведение карты.

Предоставляет заготовленные поведения на действия для карты.

Замена для типов карт:

- NumberBehavior: Стандартное поведение всех карт Uno.
- TurnBehavior: Пропуск хода для следующего игрока.
- ReverseBehavior: Разворот порядка ходов.
- TakeBehavior: Взятие карт для следующего игрока.
- WildColorBehavior: Выбор цвета для карты.
- WildTakeBehavior: Выбор цвета и взятие карт для следующего игрока.

Особые поведения:

- TwistBehavior: Обмен картами между двумя игроками.
- RotateBehavior: Обмен картами между всеми игроками.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from loguru import logger

from mau.enums import CardColor, GameEvents, GameState

if TYPE_CHECKING:
    from mau.deck.card import UnoCard
    from mau.game.game import UnoGame


class BaseBehavior(ABC):
    """базовое поведение карты.

    К каждой карте можно привязать поведение, которое будет определять
    её действия на некоторые игровые события.
    Например при использовании карты они может пропустить игрока,
    развернуть порядок ходов или увеличить счётчик взятия карт.

    Определяет интерфейс поведения карты на игровые действия.
    """

    name = "base"
    cost = 0

    @abstractmethod
    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Активное действие карты во время её разыгрывания.

        Вызывается, когда игрок кладёт кладёт верхнюю карту на верх
        колоды.

        Args:
            card: Для какой карты было вызвано действие.
            game: В какой игре происходит действие.

        """
        pass

    @abstractmethod
    def prepare_used(self, card: "UnoCard") -> None:
        """Подготовка карты к повторному использованию.

        Args:
            card: Для какой карты вызвано действие.

        """
        pass


class NumberBehavior(BaseBehavior):
    """Базовое поведение для карт Уно.

    По умолчанию записывает действия в журнал.
    Наследники переопределяет базовое поведение.
    """

    name = "number"

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Записывает в журнал использование карты."""
        logger.debug("Use card {} in game {}", card, game)

    def prepare_used(self, card: "UnoCard") -> None:
        """Подготавливает карту к повторному использованию."""
        logger.debug("Prepare card {} in game", card)


# TODO: просто присваивать поведение вместо режима
class TwistBehavior(NumberBehavior):
    """Обмен картами с другим игроком."""

    name = "twist"

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """переходит в состояния обмена картами с другим игроком.

        Срабатывает если включено правило: `twist_hand`.
        """
        if game.rules.twist_hand.status and len(game.player.hand) > 0:
            game.set_state(GameState.TWIST_HAND)


class RotateBehavior(NumberBehavior):
    """Обмен картами между всеми игроками."""

    name = "rotate"

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Обменивает карты между всеми игроками.

        Срабатывает если включено правило: `rotate_cards`.
        """
        if game.rules.rotate_cards.status and len(game.player.hand) > 0:
            game.rotate_cards()


class TurnBehavior(NumberBehavior):
    """Пропуск следующего игрока."""

    name = "turn"
    cost = 20

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Пропускает N игроков, где N - значение карты."""
        game.skip_players(card.value)


class ReverseBehavior(NumberBehavior):
    """Разворот порядка ходов."""

    name = "reverse"
    cost = 20

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Разворачивает порядок ходов в игре.

        Если осталось 2 игрока, действует как пропуск следующего игрока.
        """
        if len(game.pm) == 2:  # noqa
            game.skip_players()
        else:
            game.reverse = not game.reverse
            logger.info("Reverse flag now {}", game.reverse)


class TakeBehavior(NumberBehavior):
    """Взять карты для следующего игрока."""

    name = "take"
    cost = 20

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Увеличивает счётчик взятия карт на значение карты."""
        game.take_counter += card.value
        logger.info(
            "Take counter increase by {} now {}", card.value, game.take_counter
        )


# Дикие карты
# ===========


class BaseWildBehavior(NumberBehavior):
    """Поведение диких карт.

    После возвращения в колоду их цвет возвращается к чёрному.
    """

    name = "wild"
    cost = 50

    def prepare_used(self, card: "UnoCard") -> None:
        """Возвращает цвет карты в норму."""
        logger.debug("Prepare card {} in game", card)
        card.color = CardColor.BLACK

    def _auto_select_color(self, card: "UnoCard", game: "UnoGame") -> None:
        logger.debug("Auto choose color for card")
        color_index = (game.deck.top.color + (1 if game.reverse else -1)) % 6
        card.color = CardColor(color_index)
        game.player.push_event(GameEvents.GAME_SELECT_COLOR, str(card.color))


class WildColorBehavior(BaseWildBehavior):
    """Карта выбора цвета."""

    name = "wild+color"

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Выбирает новый цвет для карты.

        - При правиле `auto_choose_color` сам выбирает цвет.
        - При правиле `random_color` выбирает случайный цвет.
        - Иначе переходит в состояние выбора цвета.
        """
        if game.rules.auto_choose_color.status:
            self._auto_select_color(card, game)
        elif not game.rules.random_color.status:
            game.set_state(GameState.CHOOSE_COLOR)


class WildTakeBehavior(BaseWildBehavior):
    """Выбор цвета и взятие карт.

    Представляет собой комбинацию из поведения взятия и выбора цвета.
    Использовать можно только в случаях, когда нет других карт.
    Иначе выставляет флаг блефа в True.
    Следующий игрок сможет проверить  игрока на честность.
    """

    name = "wild+take"

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Выбирает новый цвет для карты и увеличивает счётчик взятия.

        Устанавливает флаг блефа для текущего игрока.

        - При правиле `auto_choose_color` сам выбирает цвет.
        - При правиле `random_color` выбирает случайный цвет.
        - Иначе переходит в состояние выбора цвета.
        """
        if game.rules.auto_choose_color.status:
            self._auto_select_color(card, game)
        elif not game.rules.random_color.status:
            game.set_state(GameState.CHOOSE_COLOR)

        game.take_counter += card.value
        game.bluff_player = (game.player, game.player.is_bluffing())
