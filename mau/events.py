"""Обработчик игровых событий."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from mau.enums import GameEvents

if TYPE_CHECKING:
    from mau.game import UnoGame
    from mau.player import Player


@dataclass(slots=True, frozen=True)
class Event:
    """Игровое событие.

    Описывает некоторое действие, происходящее во время игры.
    Содержит в себе подробную информацию о произошедшем.
    Игровые события попадают в обработчик событий.
    """

    game: "UnoGame"
    player: "Player"
    event_type: GameEvents
    data: str


class BaseEventHandler(ABC):
    """Базовый обработчик событий.

    Определяет интерфейс взаимодействия с событиями.
    """

    @abstractmethod
    def push(self, event: Event) -> None:
        """Отравляет событие в обработчик."""
        pass


class DebugEventHandler(BaseEventHandler):
    """Отладочный обработчик событий.

    Используется во время тестирования.
    Отправляет все события на печать в консоль.
    """

    def push(self, event: Event) -> None:
        """Отправляет события на печать в журнал."""
        logger.info(event)
