"""Игровой журнал событий.

Игровой журнал используется чтобы отслеживать состояние игры и отправлять его
в чат.
"""

from datetime import datetime
from typing import TYPE_CHECKING, NamedTuple

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, Message

if TYPE_CHECKING:
    from maubot.uno.game import UnoGame

# Вспомогательные классы
# ======================

# PRIORITY_ICONS = ("⚙️", "☕", "🍰", "👀", "⚠️")

# class EventPriority(IntEnum):
#     """Приоритет события.

#     У каждого события есть некоторый приоритет, который определяет
#     насколько это событие важно.
#     Если сообщение содержит приоритетные события, оно не будет удалено.

#     - DEBUG: Отладочная информация для разработки
#     - INFO: Основные события по ходу игры
#     - SUCCESS: Более важные действие, как например взятие карт.
#     - WARNING: Контролируемые проблемы, как например опустошение колоды.
#     - ERROR: Ошибки во время работы, которые не удаётся решить самому.
#     """

#     DEBUG = 0
#     INFO = 1
#     SUCCESS = 2
#     WARNING = 3
#     ERROR = 4

#     def __str__(self) -> str:
#         """представление приоритета в виде символа."""
#         return PRIORITY_ICONS[self.value]

class Event(NamedTuple):
    """Запись об игровом событии.

    Содержит некоторую цельную запись о ходе игры.
    Примером события может служить взятие карт игроком, специальные
    предложения и так далее.

    Каждое событие содержит некоторую полезную информацию о себе.
    Когда оно было совершено, кто был инициатором, насколько оно важное.
    """

    date: datetime
    text: str
    # icon: str | None
    # priority: EventPriority

    def __str__(self) -> str:
        """Представление события в виде строки."""
        # icon = self.icon if self.icon is not None else self.priority
        return f"{self.text}\n"


# Основной класс
# ==============

class Journal:
    """Класс журнала игровых событий.

    Используется для отслеживания статуса игры и оправки игровых
    событий в связанный с игрой чат.
    Каждый журнал привязывается к конкретной игре и обновляется в
    зависимости от действий участников.
    """

    def __init__(self, game: 'UnoGame', bot: Bot):
        self.game: UnoGame = game
        self.bot: Bot = bot
        self.events: list[Event] = []
        self.reply_markup: InlineKeyboardMarkup | None = None
        self.message: Message | None = None

    # Управление журналом
    # ===================

    def add(self,
        text: str,
        # icon: str | None = None,
        # priority: EventPriority | int = EventPriority.INFO
    ) -> None:
        """Добавляет новое событие в журнал."""
        self.events.append(Event(
            date=datetime.now(),
            text=text,
            # icon=icon,
            # priority=priority
        ))

    # def get_event(self, index: int) -> Event | None:
    #     pass

    # def edit_event(self, index: int, event: Event) -> None:
    #     pass

    # def remove_event(self, index: int) -> None:
    #     pass

    def set_markup(self,
        reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        self.reply_markup = reply_markup

    def get_journal_message(self):
        res = ""
        for event in self.events:
            res += str(event)
        return res

    # async def delete_journal(self):
    #     if self.message is None:
    #         return

    #     max_priority = max(self.events, key=lambda event: event.priority)
    #     if max_priority > 1:
    #         return

    #     await self.message.delete()

    async def send_journal(self):
        journal_message = self.get_journal_message()
        if self.message is None:
            self.message = await self.bot.send_message(
                chat_id=self.game.chat_id,
                text=journal_message,
                reply_markup=self.reply_markup
            )
        else:
            await self.message.edit_text(
                text=journal_message,
                reply_markup=self.reply_markup
            )

    def clear(self) -> None:
        """Очищает журнал событий."""
        # await self.delete_journal()
        self.events.clear()
        self.reply_markup = None
        self.message = None


    # Магические методы
    # =================

    def __len__(self) -> int:
        """Возвращает количество записей в журнале."""
        return len(self.events)

    def __getitem__(self, i: int) -> Event:
        """Получает событие по индексу."""
        return self.events[i]

    def __setitem__(self, i: int, event: Event) -> None:
        """Изменяет событие по индексу."""
        if not isinstance(event, Event):
            return ValueError("Journal can only contains Event instances")
        self.events[i] = event
