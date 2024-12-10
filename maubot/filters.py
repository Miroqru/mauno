from aiogram.filters import Filter
from aiogram.types import CallbackQuery

from maubot.uno.game import UnoGame
from maubot.uno.player import Player


class NowPlaying(Filter):
    async def __call__(
        self,
        query: CallbackQuery,
        game: UnoGame | None,
        player: Player | None
    ):
        if game is None or player is None:
            await query.answer("🍉 А вы точно сейчас играете?")
            return False

        if game.player == player:
            return True
        elif game.rules.ahead_of_curve:
            return True
        else:
            await query.answer("🍉 А вы точно сейчас ходите?")
