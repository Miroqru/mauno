"""Обработчик игровых событий движка."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from loguru import logger

from mau.card import BaseCard
from mau.events import BaseEventHandler, Event, GameEvents
from maubot.config import stickers

FuncType = Callable[..., Any] | Callable[..., Awaitable[Any]]

T = TypeVar("T", bound=FuncType)


class EventRouter:
    """Привязывает обработчики к конкретным событиям."""

    def __init__(self) -> None:
        self._handlers: dict[GameEvents, FuncType] = {}

    async def process(self, event: Event, journal: "MessageJournal") -> None:
        """Обрабатывает пришедшее событие."""
        handler = self._handlers.get(event.event_type)

        if handler is None:
            logger.warning("Unprocessed event: {}", event)
            return None

        if asyncio.iscoroutinefunction(handler):
            await handler(event, journal)
        else:
            handler(event, journal)

    def handler(self, event: GameEvents) -> Callable:
        """Декоратор для добавления новых обработчиков событий."""

        def wrapper(func: T) -> T:
            self._handlers[event] = func
            return func

        return wrapper


class MessageJournal(BaseEventHandler):
    """Обрабатывает события в рамках Telegram бота."""

    def __init__(self, bot: Bot, room_id: str, router: EventRouter) -> None:
        self.lobby_message: Message | None = None
        self.room_message: Message | None = None
        self.message_buffer: list[str] = []

        self.default_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎮 Разыграть 🃏",
                        switch_inline_query_current_chat="",
                    )
                ]
            ]
        )

        self.markup: InlineKeyboardMarkup | None = self.default_markup
        self._loop = asyncio.get_running_loop()
        self.bot = bot
        self.room_id = room_id
        self.router = router

    def push(self, event: Event) -> None:
        """Обрабатывает входящие события."""
        logger.info("Push event: {}", event)
        self._loop.create_task(self.router.process(event, self))

    # Отправка сообщений
    # ==================

    async def send_lobby(
        self, message: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        """Отправляет сообщение-лобби о начале новой игры."""
        if self.lobby_message is None:
            lobby_message = await self.bot.send_message(
                text=message,
                chat_id=self.room_id,
                reply_markup=reply_markup,
            )
            if isinstance(lobby_message, Message):
                self.lobby_message = lobby_message

        else:
            await self.lobby_message.edit_text(
                text=message,
                reply_markup=reply_markup,
            )

    async def send(self) -> None:
        """Отправляет журнал в чат.

        Если до этого журнал не отправлялся, будет создано отправлено
        новое сообщение с журналом.
        Если же журнал привязан, то изменится текст сообщения.
        По умолчанию журнал очищается при каждом новом ходе игрока.
        """
        if len(self.message_buffer) == 0:
            return None

        if self.room_message is None:
            self.room_message = await self.bot.send_message(
                chat_id=self.room_id,
                text="\n".join(self.message_buffer),
                reply_markup=self.markup,
            )
        else:
            await self.room_message.edit_text(
                text="\n".join(self.message_buffer),
                reply_markup=self.markup,
            )

    async def send_card(self, card: BaseCard) -> None:
        """Отправляет карту как стикер."""
        await self.bot.send_sticker(
            chat_id=self.room_id,
            sticker=stickers.normal[card.to_str()],
        )

    def clear(self) -> None:
        """Очищает буфер событий и сбрасывает клавиатуру."""
        self.message_buffer.clear()
        self.markup = self.default_markup
        self.lobby_message = None
        self.room_message = None

    def set_markup(self, markup: InlineKeyboardMarkup | None) -> None:
        """Устанавливает клавиатуру для игровых событий."""
        self.markup = markup

    def add(self, text: str) -> None:
        """Добавляет новую запись в буфер сообщений."""
        self.message_buffer.append(text)

    # TODO: Удаление журнала чтобы было меньше сообщений
    # async def delete_journal(self):
    #     if self.message is None:
    #         return

    #     max_priority = max(self.events, key=lambda event: event.priority)
    #     if max_priority > 1:
    #         return

    #     await self.message.delete()
