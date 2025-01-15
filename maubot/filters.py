"""Фильтры бота.

Фильтры используются чтобы пропускать или не пропускать события к
обработчикам.
Все фильтры представлены в одном месте для более удобного импорта.
Поскольку могут использоваться не в одном роутере.
"""

from aiogram.filters import Filter
from aiogram.types import CallbackQuery

from maubot.uno.game import UnoGame
from maubot.uno.player import Player


class NowPlaying(Filter):
    """Фильтр текущего игрока.

    Проверяет может ли вызвавший событие игрок сделать действие.
    Данный фильтр используется в игровых кнопках, как например выбор
    цвета, обмен руками или револьвер.
    Чтобы не позволить другим игрокам вмещаться в игру.

    Однако если пожелаете, это тоже можно регулировать при помощи
    игровых режимов.
    """

    async def __call__(
        self,
        query: CallbackQuery,
        game: UnoGame | None,
        player: Player | None
    ) -> bool:
        """Проверяет что текущий игрок имеет право сделать ход."""
        if game is None or player is None:
            await query.answer("🍉 А вы точно сейчас играете?")
            return False

        if game.player == player:
            return True
        elif game.rules.ahead_of_curve:
            return True
        await query.answer("🍉 А вы точно сейчас ходите?")
        return False

