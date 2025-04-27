"""Игровой контекст.

Вспомогательные функция для получения игрового контекста.
"""

from dataclasses import dataclass

from aiogram.types import (
    CallbackQuery,
    ChosenInlineResult,
    InlineQuery,
    Message,
)

from mau.game.game import UnoGame
from mau.game.player import Player
from mau.session import SessionManager


@dataclass(frozen=True, slots=True)
class GameContext:
    """Игровой контекст.

    Передаётся в обработчики команд и фильтры.
    Содержит экземпляр активной игры, а также игрока.
    """

    game: UnoGame | None
    player: Player | None


def get_context(
    sm: SessionManager,
    event: Message | CallbackQuery | InlineQuery | ChosenInlineResult,
) -> GameContext:
    """Получает игровой контекст."""
    player = (
        sm.player(str(event.from_user.id))
        if event.from_user is not None
        else None
    )

    if player is not None:
        return GameContext(game=player.game, player=player)

    if isinstance(event, Message):
        game = sm.room(str(event.chat.id))

    elif isinstance(event, CallbackQuery) and event.message is not None:
        game = sm.room(str(event.message.chat.id))

    else:
        game = None

    return GameContext(game=game, player=None)
