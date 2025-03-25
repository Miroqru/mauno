"""Обработчик игровых событий."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from mau.game import UnoGame
    from mau.player import Player

# Вспомогательные классы
# ======================


class GameEvents(StrEnum):
    """Все варианты игровых событий.

    Типы событий могут сопровождаться уточняющими данными.

    Игровая сессия:
    - session_start: Началась новая сессия.
    - session_end: Закончилась сессия.
    - session_join: Игрок присоединился к сессии.
    - session_leave: Игрок покинул сессию.
    - session_update: Данные комнаты обновлены. Правила, информация, владелец.

    Игра:
    - game_start: Началась новая игра.
    - game_end: Игра завершилась.
    - game_join: Игрой зашёл в игру.
    - game_leave: Игрок вышел, проиграл, выиграл, был исключён, застрелился.
    - game_next: Переход к следующему игроку.
    - game_take: Взятие карт из колоды, также вместо револьвера.
    - game_shot: Выстрел из револьвера.
    - game_bluff: Проверка на честность прошлого игрока.
    - game_select_color: Выбор цвета для карты.
    - game_select_player: Выбор игрока для обмена картами.
    - game_push: Игрок выбросил карту.
    - game_reverse: Разворачивается порядок ходов.
    - game_turn: Переход к следующему ходу.
    - game_rotate: Обмен картами между всеми игроками.
    - game_intervention: Игрок вмешался во время игры.
    - game_uno: Крикнуть что осталась одна карта.
    - game_state: Обновление состояния игры.
    """

    # Игровые сессии
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SESSION_JOIN = "session_join"
    SESSION_LEAVE = "session_leave"
    SESSION_UPDATE = "session_update"

    # Игровые события
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_JOIN = "game_join"
    GAME_LEAVE = "game_leave"
    GAME_NEXT = "game_next"
    GAME_TAKE = "game_take"
    GAME_SHOT = "game_shot"
    GAME_BLUFF = "game_bluff"
    GAME_SELECT_COLOR = "game_select_color"
    GAME_SELECT_PLAYER = "game_select_player"
    GAME_PUSH = "game_push"
    GAME_REVERSE = "game_reverse"
    GAME_TURN = "game_turn"
    GAME_ROTATE = "game_rotate"
    GAME_INTERVENTION = "game_intervention"
    GAME_UNO = "game_uno"
    GAME_STATE = "game_state"


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
