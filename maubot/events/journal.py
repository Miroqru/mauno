"""Обработчик игровых событий движка."""

import asyncio
from collections import deque
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
        logger.debug(event)
        handler = self._handlers.get(event.event_type)

        if handler is None:
            logger.warning("No handler on: {}", event)
            return None

        await handler(event, journal)

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
        self.message_queue: deque[str] = deque(maxlen=5)

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
        logger.debug(event)
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

    async def send_message(self, text: str) -> None:
        """Отправляет сообщение в комнату."""
        return await self.bot.send_message(
            chat_id=self.room_id,
            text=text,
            reply_markup=self.markup,
        )

    async def send(self) -> None:
        """Отправляет журнал в чат.

        Если до этого журнал не отправлялся, будет создано отправлено
        новое сообщение с журналом.
        Если же журнал привязан, то изменится текст сообщения.
        По умолчанию журнал очищается при каждом новом ходе игрока.
        """
        if len(self.message_queue) == 0:
            return None

        if self.room_message is None:
            self.room_message = await self.send_message(
                text="\n".join(self.message_queue),
            )
        else:
            await self.room_message.edit_text(
                text="\n".join(self.message_queue),
                reply_markup=self.markup,
            )

    async def send_card(self, card: BaseCard) -> None:
        """Отправляет карту как стикер."""
        await self.bot.send_sticker(
            chat_id=self.room_id,
            sticker=stickers.normal[card.to_str()],
        )

    async def clear(self) -> None:
        """Очищает буфер событий и сбрасывает клавиатуру."""
        self.markup = self.default_markup
        self.lobby_message = None
        if self.room_message is not None:
            await self.room_message.delete()
            self.room_message = None

    def set_markup(self, markup: InlineKeyboardMarkup | None) -> None:
        """Устанавливает клавиатуру для игровых событий."""
        self.markup = markup

    def add(self, text: str) -> None:
        """Добавляет новую запись в буфер сообщений."""
        self.message_queue.append(text)
