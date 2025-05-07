"""Фильтры бота.

Фильтры используются чтобы пропускать или не пропускать события к
обработчикам.
Все фильтры представлены в одном месте для более удобного импорта.
Поскольку могут использоваться не в одном роутере.
"""

from aiogram.enums import ChatMemberStatus
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from maubot.config import sm
from maubot.context import get_context

NO_JOIN_MESSAGE = (
    "🍓 Для начала надо <b>зайти в комнату</b>.\n"
    "🍰 Сделать это можно командой /join.\n"
    "🔑 Если комната <b>закрыта</b> дождитесь окончания игры."
)

NO_ROOM_MESSAGE = (
    "👀 В данном чате ещё <b>нет игровой комнаты</b>.\n"
    "🍰 Вы можете <b>создайте новую</b> при помощи команды /game."
)


async def _send(event: CallbackQuery | Message, message: str) -> None:
    if isinstance(event, CallbackQuery) and event.message is not None:
        await event.message.answer(message)

    elif isinstance(event, Message):
        await event.answer(message)


async def _is_admin(event: CallbackQuery | Message) -> bool:
    if isinstance(event, Message):
        chat = event.chat
    elif isinstance(event, CallbackQuery):
        if event.message is None:
            return False
        chat = event.message.chat

    if event.from_user is None:
        return False
    member = await chat.get_member(event.from_user.id)
    return member.status in (
        ChatMemberStatus.CREATOR,
        ChatMemberStatus.ADMINISTRATOR,
    )


# Фильтры
# =======


# TODO: Может теперь ты будешь открытой игрой?
class ActiveGame(Filter):
    """Фильтр активной игры.

    Даёт гарантию что в данном чате имеется игра.
    """

    async def __call__(self, event: CallbackQuery | Message) -> bool:
        """Проверяет что игра существует."""
        if get_context(sm, event).game is None:
            await _send(event, NO_ROOM_MESSAGE)
            return False

        return True


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
            await _send(event, NO_ROOM_MESSAGE)
            return False

        if context.player is None:
            await _send(event, NO_JOIN_MESSAGE)
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
            await _send(event, NO_ROOM_MESSAGE)
            return False

        if await _is_admin(event):
            return True

        if context.player is None:
            await _send(event, NO_JOIN_MESSAGE)
            return False

        if context.player != context.game.owner:
            await _send(
                event,
                "🔑 Выполнить это действие может только создатель комнаты.",
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
        if ctx.player is None or not ctx.player.can_play or ctx.game is None:
            await event.answer("🍉 А вы точно сейчас играете?")
            return False

        if ctx.player != ctx.game.player:
            ctx.game.pm.set_cp(ctx.player)

        return True
