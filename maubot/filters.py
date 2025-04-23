"""Фильтры бота.

Фильтры используются чтобы пропускать или не пропускать события к
обработчикам.
Все фильтры представлены в одном месте для более удобного импорта.
Поскольку могут использоваться не в одном роутере.
"""

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from maubot.config import sm
from maubot.context import get_context
from maubot.messages import NO_JOIN_MESSAGE, NO_ROOM_MESSAGE


class ActiveGame(Filter):
    """Фильтр активной игры.

    Даёт гарантию что в данном чате имеется игра.
    """

    async def __call__(self, event: CallbackQuery | Message) -> bool:
        """Проверяет что игра существует."""
        context = get_context(sm, event)
        if context.game is not None:
            return True

        if isinstance(event, CallbackQuery) and event.message is not None:
            await event.message.answer(NO_ROOM_MESSAGE)

        elif isinstance(event, Message):
            await event.answer(NO_ROOM_MESSAGE)

        return False


class ActivePlayer(Filter):
    """Фильтр активного игрока.

    Нет, он просто даёт гарантии что есть как игра, так и игрок.
    Поскольку игрок не может существовать без игры, наличие игры также
    автоматические проверяется.
    """

    async def __call__(self, event: CallbackQuery | Message) -> bool:
        """Проверяет что данный игрок есть в игре."""
        context = get_context(sm, event)

        if context.game is None:
            if isinstance(event, CallbackQuery) and event.message is not None:
                await event.message.answer(NO_ROOM_MESSAGE)

            elif isinstance(event, Message):
                await event.answer(NO_ROOM_MESSAGE)
            return False

        if context.player is None:
            if isinstance(event, CallbackQuery) and event.message is not None:
                await event.message.answer(NO_JOIN_MESSAGE)

            elif isinstance(event, Message):
                await event.answer(NO_JOIN_MESSAGE)
            return False

        return True


class GameOwner(Filter):
    """Фильтр создателя комнаты.

    Помимо проверки на наличие комнаты и игрока также проверяет
    чтобы вызвавший команду игрок был администратором комнаты.
    Это полезно в некоторых административных командах.
    """

    async def __call__(self, event: CallbackQuery | Message) -> bool:
        """Проверяет что данный игрок создатель комнаты."""
        context = get_context(sm, event)

        if context.game is None:
            if isinstance(event, CallbackQuery) and event.message is not None:
                await event.message.answer(NO_ROOM_MESSAGE)

            elif isinstance(event, Message):
                await event.answer(NO_ROOM_MESSAGE)
            return False

        if context.player is None:
            if isinstance(event, CallbackQuery) and event.message is not None:
                await event.message.answer(NO_JOIN_MESSAGE)

            elif isinstance(event, Message):
                await event.answer(NO_JOIN_MESSAGE)
            return False

        if context.player != context.game.owner:
            if isinstance(event, CallbackQuery) and event.message is not None:
                await event.message.answer(
                    "🔑 Выполнить эту команду может только создатель комнаты."
                )

            elif isinstance(event, Message):
                await event.answer(
                    "🔑 Выполнить эту команду может только создатель комнаты."
                )
            return False

        return True


class NowPlaying(Filter):
    """Фильтр текущего игрока.

    Проверяет может ли вызвавший событие игрок сделать действие.
    Данный фильтр используется в игровых кнопках, как например выбор
    цвета, обмен руками или револьвер.
    Чтобы не позволить другим игрокам вмещаться в игру.

    Однако если пожелаете, это тоже можно регулировать при помощи
    игровых режимов.
    """

    async def __call__(self, event: CallbackQuery) -> bool:
        """Проверяет что текущий игрок имеет право сделать ход."""
        ctx = get_context(sm, event)
        if ctx.player is None or not ctx.player.can_play:
            await event.answer("🍉 А вы точно сейчас играете?")
            return False
        return True
