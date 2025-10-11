"""Поведение карты.

Предоставляет класс поведения и базовые callback для них.
"""

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from loguru import logger

from mau.enums import GameEvents, GameState
from mau.events import dataclass
from mau.rules import GameRules

if TYPE_CHECKING:
    from mau.deck.card import MauCard
    from mau.game.game import MauGame

Callback = Callable[["MauGame", "MauCard"], None]


def _auto_select_color(card: "MauCard", game: "MauGame") -> None:
    logger.debug("Auto choose color for card")
    color_index = game.deck.colors.index(game.deck.top.color)
    if game.reverse:
        color_index -= 1
    else:
        color_index += 1
    color_index %= len(game.deck.colors)
    card.color = game.deck.colors[color_index]
    game.player.dispatch(GameEvents.GAME_SELECT_COLOR, card.color)


def log(game: "MauGame", card: "MauCard") -> None:
    """Записывает действие с картой."""
    logger.debug("Use card {} in game {}", card, game)


# TODO: Просто поведение, без определённого режима
def twist(game: "MauGame", card: "MauCard") -> None:
    """переходит в состояния обмена картами с другим игроком.

    Срабатывает если включено правило: `twist_hand`.
    """
    if game.rules.status(GameRules.twist_hand) and len(game.player.hand) > 1:
        game.set_state(GameState.TWIST_HAND)


# TODO: Просто поведение, без определённого режима
def rotate(game: "MauGame", card: "MauCard") -> None:
    """Обменивает карты между всеми игроками.

    Срабатывает если включено правило: `rotate_cards`.
    """
    if game.rules.status(GameRules.rotate_cards) and len(game.player.hand) > 1:
        game.rotate_cards()


def turn(game: "MauGame", card: "MauCard") -> None:
    """Пропускает N игроков, где N - значение карты."""
    game.skip_players(card.value)


def reverse(game: "MauGame", card: "MauCard") -> None:
    """Разворачивает порядок ходов в игре.

    Если осталось 2 игрока, действует как пропуск следующего игрока.
    """
    if len(game.pm) == 2:  # noqa: PLR2004
        game.skip_players()
    else:
        game.reverse = not game.reverse
        logger.info("Reverse flag now {}", game.reverse)


def take(game: "MauGame", card: "MauCard") -> None:
    """Увеличивает счётчик взятия карт на значение карты."""
    logger.info(
        "Take counter increase by {} now {}", card.value, game.take_counter
    )
    game.take_counter += card.value


def take_bluff(game: "MauGame", card: "MauCard") -> None:
    """Выбирает новый цвет для карты и увеличивает счётчик взятия.

    Устанавливает флаг блефа для текущего игрока.

    - При правиле `auto_choose_color` сам выбирает цвет.
    - При правиле `random_color` выбирает случайный цвет.
    - Иначе переходит в состояние выбора цвета.
    """
    logger.info(
        "Take counter increase by {} now {}", card.value, game.take_counter
    )
    game.take_counter += card.value
    game.bluff_player = (game.player.user_id, game.player.is_bluffing())


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


@dataclass(slots=True, frozen=True)
class CardBehavior:
    """Поведение карты.

    Args:
        name: Название поведения.
        cost: СТоимость такой карты.
        use: Действия при использовании карты.
        cover: Действия при освобождении карты.
        on_counter: Можно использовать при активном счётчике карт.

    """

    name: str
    cost: int
    use: Sequence[Callback]
    cover: Sequence[Callback]
    on_counter: bool = False
