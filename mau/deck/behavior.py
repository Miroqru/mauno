"""Поведение карты.

Предоставляет класс поведения и базовые callback для них.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from mau.enums import GameState
from mau.events import GameEvents
from mau.rules import GameRules

if TYPE_CHECKING:
    from mau.deck.card import MauCard
    from mau.game.game import MauGame

Callback = Callable[["MauGame", "MauCard"], None]


@dataclass(slots=True, frozen=True)
class CardBehavior:
    """Описание поведения для карты.

    Поведение это набор уникальных параметров и действия для карты.
    """

    name: str
    """Уникальное имя поведения.

    Карты с одинаковым поведением (и значением) могут покрыть друг друга.
    """

    use: Sequence[Callback]
    """Действия, которые будут выполняться при использовании карты."""

    cover: Sequence[Callback]
    """Действия, которые будут выполняться когда карту покроют другой картой."""

    on_counter: bool = False
    """Можно ли использовать карту при не нулевом счётчике карт.

    Этот флаг нужен для карт типа +2/+4, когда нужно их использовать.
    """


def _auto_select_color(card: "MauCard", game: "MauGame") -> None:
    logger.debug("Auto choose color for card")
    color_index = game.deck.colors.index(game.deck.top.color)
    if game.pm.reverse == 1:
        color_index += 1
    else:
        color_index -= 1
    color_index %= len(game.deck.colors)
    card.color = game.deck.colors[color_index]
    game.player.dispatch(GameEvents.GAME_SELECT_COLOR, card.color)


def log(game: "MauGame", card: "MauCard") -> None:
    """Записывает действие с картой."""
    logger.debug("Use card {} in game {}", card, game)


def twist(game: "MauGame", card: "MauCard") -> None:  # noqa: ARG001
    """переходит в состояния обмена картами с другим игроком."""
    if len(game.player.hand) > 1:
        game.set_state(GameState.TWIST_HAND)


def rotate(game: "MauGame", card: "MauCard") -> None:  # noqa: ARG001
    """Обменивает карты между всеми игроками."""
    if len(game.player.hand) > 1:
        game.pm.rotate_cards()
        game.player.dispatch(GameEvents.GAME_ROTATE, None)


def turn(game: "MauGame", card: "MauCard") -> None:
    """Пропускает N игроков, где N - значение карты."""
    game.pm.next(card.value)


def reverse(game: "MauGame", card: "MauCard") -> None:  # noqa: ARG001
    """Разворачивает порядок ходов в игре.

    Если осталось 2 игрока, действует как пропуск следующего игрока.
    """
    if len(game.pm) == 2:
        game.pm.next()
    else:
        game.set_reverse()


def take(game: "MauGame", card: "MauCard") -> None:
    """Увеличивает счётчик взятия карт на значение карты."""
    logger.info("Take counter increase by {} now {}", card.value, game.take_counter)
    game.take_counter += card.value


def take_bluff(game: "MauGame", card: "MauCard") -> None:
    """Выбирает новый цвет для карты и увеличивает счётчик взятия.

    Устанавливает флаг блефа для текущего игрока.

    - При правиле `auto_choose_color` сам выбирает цвет.
    - При правиле `random_color` выбирает случайный цвет.
    - Иначе переходит в состояние выбора цвета.
    """
    logger.info("Take counter increase by {} now {}", card.value, game.take_counter)
    game.take_counter += card.value
    game.bluff_state = (game.player.id, game.player.is_bluffing())


def reset_color(game: "MauGame", card: "MauCard") -> None:
    """Возвращает цвет карты в норму."""
    logger.debug("Prepare card {} in game", card)
    card.color = game.deck.wild_color


def set_color(game: "MauGame", card: "MauCard") -> None:
    """Выбирает новый цвет для карты.

    - При правиле `auto_choose_color` сам выбирает цвет.
    - При правиле `random_color` выбирает случайный цвет.
    - Иначе переходит в состояние выбора цвета.
    """
    if game.rules.status(GameRules.auto_choose_color):
        _auto_select_color(card, game)
    elif not game.rules.status(GameRules.random_color):
        game.set_state(GameState.CHOOSE_COLOR)
