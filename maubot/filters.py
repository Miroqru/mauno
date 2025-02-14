"""Фильтры бота.

Фильтры используются чтобы пропускать или не пропускать события к
обработчикам.
Все фильтры представлены в одном месте для более удобного импорта.
Поскольку могут использоваться не в одном роутере.
"""

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from mau.game import UnoGame
from mau.player import Player
from maubot.messages import NO_JOIN_MESSAGE, NO_ROOM_MESSAGE


class ActiveGame(Filter):
    """Фильтр активной игры.

    Даёт гарантию что в данном чате имеется игра.
    """

    async def __call__(
        self,
        query: CallbackQuery,
        message: Message,
        game: UnoGame | None,
    ) -> bool:
        """Проверяет что игра существует."""
        if game is not None:
            return True

        if query is not None and query.message is not None:
            await query.message.answer(NO_ROOM_MESSAGE)
        elif message is not None:
            await message.answer(NO_ROOM_MESSAGE)

        return False


class ActivePlayer(Filter):
    """Фильтр активного игрока.

    Нет, он просто даёт гарантии что есть как игра, так и игрок.
    Поскольку игрок не может существовать без игры, наличие игры также
    автоматические проверяется.
    """

    async def __call__(
        self,
        query: CallbackQuery,
        message: Message,
        game: UnoGame | None,
        player: Player | None,
    ) -> bool:
        """Проверяет что данный игрок есть в игре."""
        if game is None:
            if query is not None and query.message is not None:
                await query.message.answer(NO_ROOM_MESSAGE)
            elif message is not None:
                await message.answer(NO_ROOM_MESSAGE)
            return False

        if player is None:
            if query is not None and query.message is not None:
                await query.message.answer(NO_JOIN_MESSAGE)
            elif message is not None:
                await message.answer(NO_JOIN_MESSAGE)
            return False

        return True


class GameOwner(Filter):
    """Фильтр создателя комнаты.

    Помимо проверки на наличие комнаты и игрока также проверяет
    чтобы вызвавший команду игрок был администратором комнаты.
    Это полезно в некоторых административных командах.
    """

    async def __call__(
        self,
        query: CallbackQuery,
        message: Message,
        game: UnoGame | None,
        player: Player | None,
    ) -> bool:
        """Проверяет что данный игрок создатель комнаты."""
        if game is None:
            if query is not None and query.message is not None:
                await query.message.answer(NO_ROOM_MESSAGE)
            elif message is not None:
                await message.answer(NO_ROOM_MESSAGE)
            return False

        if player is None:
            if query is not None and query.message is not None:
                await query.message.answer(NO_JOIN_MESSAGE)
            elif message is not None:
                await message.answer(NO_JOIN_MESSAGE)
            return False

        if player != game.owner:
            if query is not None and query.message is not None:
                await query.message.answer(
                    "🔑 Выполнить эту команду может только создатель комнаты."
                )
            elif message is not None:
                await message.answer(
                    "🔑 Выполнить эту команду может только создатель комнаты."
                )
            return False

        return True


# TODO: Возможно он даже не работает нормально, да вот только почему??
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
        self, query: CallbackQuery, game: UnoGame | None, player: Player | None
    ) -> bool:
        """Проверяет что текущий игрок имеет право сделать ход."""
        if game is None or player is None:
            await query.answer("🍉 А вы точно сейчас играете?")
            return False

        if game.player == player or game.rules.ahead_of_curve.status:
            return True

        await query.answer("🍉 А сейчас точно ваш ход?")
        return False
