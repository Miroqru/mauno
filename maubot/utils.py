from dataclasses import dataclass

from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Update,
)
from icecream import ic

from mau.game import UnoGame
from mau.player import Player
from mau.session import SessionManager


@dataclass(frozen=True, slots=True)
class GameContext:
    game: UnoGame | None
    player: Player | None


def get_context(sm: SessionManager, event: Update) -> GameContext:
    if isinstance(event, Message | ChatMemberUpdated):
        game = sm.games.get(str(event.chat.id))
        ic(game, sm.games)
    elif isinstance(event, CallbackQuery):
        if event.message is None:
            chat_id = sm.user_to_chat.get(str(event.from_user.id))
            game = None if chat_id is None else sm.games.get(chat_id)
            ic(game, sm.user_to_chat, chat_id)
        else:
            game = sm.games.get(event.message.chat.id)
            ic(game, sm.games)
    elif isinstance(event, InlineQuery | ChosenInlineResult):
        chat_id = sm.user_to_chat.get(str(event.from_user.id))
        game = None if chat_id is None else sm.games.get(chat_id)
        ic(game, chat_id, sm.user_to_chat)
    else:
        raise ValueError("Unknown update type")

    player = (
        None
        if game is None or event.from_user is None
        else game.get_player(str(event.from_user.id))
    )
    ic(game)
    return GameContext(game=game, player=player)
