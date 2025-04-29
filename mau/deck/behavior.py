"""Поведение карты."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from loguru import logger

from mau.enums import CardColor, GameEvents, GameState

if TYPE_CHECKING:
    from mau.deck.card import UnoCard
    from mau.game.game import UnoGame


class BaseBehavior(ABC):
    """Поведение карты."""

    @abstractmethod
    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Активное действие карты во время её разыгрывания."""
        pass

    @abstractmethod
    def prepare_used(self, card: "UnoCard") -> None:
        """Подготовка карты к повторному использованию."""
        pass


class UnoBehavior(BaseBehavior):
    """Стандартное поведение для карты Уно."""

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Записывает в журнал использование карты."""
        logger.debug("Use card {} in game {}", card, game)

    def prepare_used(self, card: "UnoCard") -> None:
        """Подготавливает карту к повторному использованию."""
        logger.debug("Prepare card {} in game", card)


class TwistBehavior(UnoBehavior):
    """Обмен руками с другим игроком."""

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """переходит в состояния обмена руками с другим игроком."""
        if game.rules.twist_hand.status:
            game.set_state(GameState.TWIST_HAND)


class RotateBehavior(UnoBehavior):
    """Обмен картами между всеми игроками."""

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Обменивает карты между всеми игроками, если включено правило."""
        if game.rules.rotate_cards.status:
            game.rotate_cards()


class TurnBehavior(UnoBehavior):
    """Пропуск игрока."""

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Пропускает N игроков, где N - значение карты."""
        logger.info("Skip {} players", card.value)
        game.skip_players(card.value)


class ReverseBehavior(UnoBehavior):
    """Разворот порядка ходов."""

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Разворачивает порядок ходов в игре.

        Если осталось 2 игрока, действует как карта пропуска хода.
        """
        if len(game.pm) == 2:  # noqa
            game.skip_players()
        else:
            game.reverse = not game.reverse
            logger.info("Reverse flag now {}", game.reverse)


class TakeBehavior(UnoBehavior):
    """Взятие карт."""

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Увеличивает счётчик взятия карт на значение карты."""
        game.take_counter += card.value
        logger.info(
            "Take counter increase by {} now {}", card.value, game.take_counter
        )


# Дикие карты
# ===========


class WildBehavior(UnoBehavior):
    """Поведение диких карт.

    После использования их цвет возвращается к обычному.
    """

    def prepare_used(self, card: "UnoCard") -> None:
        """Возвращает цвет карты в норму."""
        logger.debug("Prepare card {} in game", card)
        card.color = CardColor.BLACK

    def _auto_select_color(self, card: "UnoCard", game: "UnoGame") -> None:
        logger.debug("Auto choose color for card")
        color_index = (game.deck.top.color + (1 if game.reverse else -1)) % 4
        card.color = CardColor(color_index)
        game.player.push_event(GameEvents.GAME_SELECT_COLOR, str(card.color))


class ColorBehavior(WildBehavior):
    """Выбор цвета для карты."""

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Выбирает новый цвет для карты."""
        if game.rules.auto_choose_color.status:
            self._auto_select_color(card, game)
        elif not game.rules.random_color.status:
            game.set_state(GameState.CHOOSE_COLOR)


class ColorTakeBehavior(WildBehavior):
    """Выбор цвета и взятие карт.

    Представляет собой комбинацию из карты взятия и выбора цвета.
    Использоваться можно только в случаях, когда нет других карт.
    Выставляет флаг блефа.
    Следующий игрок сможет проверить текущего игрока на честность.
    """

    def use(self, card: "UnoCard", game: "UnoGame") -> None:
        """Выбирает новый цвет для карты."""
        if game.rules.auto_choose_color.status:
            self._auto_select_color(card, game)
        elif not game.rules.random_color.status:
            game.set_state(GameState.CHOOSE_COLOR)

        game.take_counter += card.value
        game.bluff_player = (game.player, game.player.is_bluffing())
