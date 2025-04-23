"""Обработчик игровых событий."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from mau.enums import GameEvents

if TYPE_CHECKING:
    from mau.game import UnoGame
    from mau.player import Player

# Вспомогательные классы
# ======================


@dataclass(slots=True, frozen=True)
class Event:
    """Игровое событие."""

    room_id: str
    player: "Player"
    event_type: GameEvents
    data: str
    game: "UnoGame"


# Абстрактные классы
# ==================


class BaseEventHandler(ABC):
    """Базовый обработчик событий.

    Пришёл на смену устаревшему журналу событий.
    Наследники реализуют способ обработки игровых событий по своему
    усмотрению.
    """

    @abstractmethod
    def push(self, event: Event) -> None:
        """Отравляет событие в обработчик."""
        pass


class DebugEventHandler(BaseEventHandler):
    """Пример обработчика событий, отправляет изменения в консоль."""

    def push(self, event: Event) -> None:
        """Отравляет событие в консоль."""
        logger.info(event)
