"""Обработка игровых событий.

Предоставляет класс события и базовый обработчик событий.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from mau.enums import GameEvents

if TYPE_CHECKING:
    from mau.game.game import UnoGame
    from mau.game.player import Player


@dataclass(slots=True, frozen=True)
class Event:
    """Игровое событие.

    Когда во время игры происходит действие, создаётся класс события.
    Событие описывает исчерпывающую информацию о произошедшем:

    - Для какой игры произошло событие.
    - Какой игрок его совершил.
    - Тип события.
    - Опциональная подробная информация о событии.

    Созданные игрой события отправляются в обработчик.
    """

    game: "UnoGame"
    player: "Player"
    event_type: GameEvents
    data: str


class BaseEventHandler(ABC):
    """Базовый обработчик событий.

    При возникновении игровых события они отправляются в обработчик.
    Обработчик уже решает как поступить с этими событиями.
    Базовый класс определяет интерфейс взаимодействия с событиями.
    """

    @abstractmethod
    def push(self, event: Event) -> None:
        """Обрабатывает игровое событие.

        Это может быть отправка в консоль, веб сокет или действия бота.
        """
        pass


class DebugEventHandler(BaseEventHandler):
    """Отладочный обработчик событий.

    Используется для тестирования как заглушка.
    Все пришедшие события перенаправляются в консоль.
    Не подходит для использования, поскольку некоторое события требуют
    ответной реакции.
    """

    def push(self, event: Event) -> None:
        """Перенаправляет событие в консоль."""
        logger.info(event)
