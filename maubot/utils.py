"""Игровой контекст.

Вспомогательные функции для получения игрового контекста.
"""

from dataclasses import dataclass

from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Update,
)

from mau.game import UnoGame
from mau.player import Player
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
    event: Message | ChatMemberUpdated | CallbackQuery | Message | Update,
) -> GameContext:
    """Получает игровой контекста."""
    if isinstance(event, Message | ChatMemberUpdated):
        game = sm.games.get(str(event.chat.id))

    elif isinstance(event, CallbackQuery):
        if event.message is None:
            chat_id = sm.user_to_chat.get(str(event.from_user.id))
            game = None if chat_id is None else sm.games.get(chat_id)
        else:
            game = sm.games.get(str(event.message.chat.id))

    elif isinstance(event, InlineQuery | ChosenInlineResult):
        chat_id = sm.user_to_chat.get(str(event.from_user.id))
        game = None if chat_id is None else sm.games.get(chat_id)

    else:
        raise ValueError("Unknown update type")

    player = (
        None
        if game is None or event.from_user is None
        else game.get_player(str(event.from_user.id))
    )
    return GameContext(game=game, player=player)
