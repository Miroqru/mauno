"""Игровой журнал событий.

Игровой журнал используется чтобы отслеживать состояние игры и отправлять его
в чат.

TODO: Что за суета происходит тут в журнале?
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum
from typing import NamedTuple, overload

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# Вспомогательные классы
# ======================


class EventPriority(IntEnum):
    """Приоритет события.

    У каждого события есть некоторый приоритет, который определяет
    насколько это событие важно.
    Если сообщение содержит приоритетные события, оно не будет удалено.

    - DEBUG: Отладочная информация для разработки
    - INFO: Основные события по ходу игры
    - SUCCESS: Более важные действие, как например взятие карт.
    - WARNING: Контролируемые проблемы, как например опустошение колоды.
    - ERROR: Ошибки во время работы, которые не удаётся решить самому.
    """

    DEBUG = 0
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4


class EventAction(NamedTuple):
    """Callback кнопочки для событий журнала.

    Абстрактное представление действий, которые пользователь может
    совершить в данный момент.
    """

    text: str
    callback_data: str


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
    priority: EventPriority

    def __str__(self) -> str:
        """Представление события в виде строки."""
        return self.text


# абстрактный класс журнала
# =========================


class BaseJournal(ABC):
    """Абстрактный журнал событий.

    Позволяет записывать игровые события, а после отправлять их по надобности.
    """

    @abstractmethod
    def add(
        self, text: str, priority: EventPriority | int = EventPriority.INFO
    ) -> None:
        """Добавляет новое событие в журнал."""
        pass

    @abstractmethod
    def set_actions(self, actions: list[EventAction] | None = None) -> None:
        """Устанавливает доступные действия для журнала при отправку журнала."""
        pass

    @abstractmethod
    def get_journal_message(self) -> str:
        """Собирает сообщение журнала из всех событий."""
        pass

    @abstractmethod
    async def send_journal(self) -> None:
        """Отправляет сообщение журнала.

        Это может быть как чат telegram, так и к примеру консоль.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Очищает журнал событий."""
        pass


# Основной класс
# ==============


class TelegramJournal(BaseJournal):
    """Класс журнала игровых событий.

    Используется для отслеживания статуса игры и оправки игровых
    событий в связанный с игрой чат.
    Каждый журнал привязывается к конкретной игре и обновляется в
    зависимости от действий участников.
    """

    def __init__(self, room_id: str, bot: Bot) -> None:
        self.room_id: str = room_id
        self.bot: Bot = bot
        self.default_action = [
            InlineKeyboardButton(
                text="🎮 Разыграть 🃏", switch_inline_query_current_chat=""
            )
        ]

        self.events: list[Event] = []
        self.actions: list[EventAction | InlineKeyboardButton] | None = list(
            self.default_action
        )
        self.message: Message | None = None

    # Управление журналом
    # ===================

    def _actions_to_reply_markup(self) -> InlineKeyboardMarkup | None:
        if self.actions is None:
            return None

        inline_keyboard: list[list[InlineKeyboardButton]] = []
        for i, action in enumerate(self.actions):
            if i % 3 == 0:
                inline_keyboard.append([])

            if isinstance(action, EventAction):
                inline_keyboard[-1].append(
                    InlineKeyboardButton(
                        text=action.text, callback_data=action.callback_data
                    )
                )
            else:
                inline_keyboard[-1].append(action)
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    def add(
        self, text: str, priority: EventPriority | int = EventPriority.INFO
    ) -> None:
        """Добавляет новое событие в журнал."""
        self.events.append(
            Event(
                date=datetime.now(), text=text, priority=EventPriority(priority)
            )
        )

    # def get_event(self, index: int) -> Event | None:
    #     pass

    # def edit_event(self, index: int, event: Event) -> None:
    #     pass

    # def remove_event(self, index: int) -> None:
    #     pass

    @overload
    def set_actions(self, actions: list[EventAction] | None = None) -> None: ...

    @overload
    def set_actions(
        self, actions: list[EventAction | InlineKeyboardButton] | None = None
    ) -> None: ...

    def set_actions(
        self,
        actions: list | None = None,
    ) -> None:
        """Устанавливает клавиатуру для бота при отправку журнала."""
        self.actions = actions

    def get_journal_message(self) -> str:
        """Собирает сообщение журнала из всех событий."""
        res = ""
        for event in self.events:
            res += f"{event}\n"
        return res

    # TODO: Удаление журнала чтобы было меньше сообщений
    # async def delete_journal(self):
    #     if self.message is None:
    #         return

    #     max_priority = max(self.events, key=lambda event: event.priority)
    #     if max_priority > 1:
    #         return

    #     await self.message.delete()

    async def send_journal(self) -> None:
        """Отправляет журнал в чат.

        Если до этого журнал не отправлялся, будет создано отправлено
        новое сообщение с журналом.
        Если же журнал привязан, то изменится текст сообщения.
        По умолчанию журнал очищается при каждом новом ходе игрока.
        """
        journal_message = self.get_journal_message()
        if self.message is None:
            self.message = await self.bot.send_message(
                chat_id=self.room_id,
                text=journal_message,
                reply_markup=self._actions_to_reply_markup(),
            )
        else:
            await self.message.edit_text(
                text=journal_message,
                reply_markup=self._actions_to_reply_markup(),
            )

    def clear(self) -> None:
        """Очищает журнал событий."""
        # await self.delete_journal()
        self.events.clear()
        self.actions = list(self.default_action)
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
            return ValueError(
                "TelegramJournal can only contains Event instances"
            )
        self.events[i] = event
