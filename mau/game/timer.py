"""игровой таймер.

Используется как для подсчёта потраченного времени.
так и для предупреждения о прошедших лимитах.
"""

from dataclasses import dataclass
from enum import IntEnum
from time import time


class TimerAlert(IntEnum):
    """Предупреждение таймера.

    Когда какой-то из лимитов был пройден, таймер возвращает об этом
    событие.
    """

    TICKS = 1
    TURN = 2
    GAME = 3


@dataclass(frozen=True, slots=True)
class TimerStat:
    """Статистика таймера.

    - game: Сколько секунд прошло с начала игры,
    - turn: Сколько секунд прошло с начала хода.
    - ticks: Сколько суммарно прошло ходов.
    - alert: Уведомление таймера.
    """

    game: int
    turn: int
    ticks: int
    alert: TimerAlert | None


class GameTimer:
    """Игровой таймер.

    Ведёт подсчёт времени, затраченного на игру, ход, записывает количество
    ходов.
    Позволяет выставлять временные ограничения или на количество ходов.

    После достижения лимитов будет выведено предупреждение.
    Обработка предупреждений происходит на стороне клиента.

    Args:
        tick_limit: Ограничение на общее количество ходов.
        turn_limit: Ограничение времени на ход.
        game_limit: Ограничение времени на игру.

    """

    def __init__(
        self, tick_limit: int = 0, turn_limit: int = 0, game_limit: int = 0
    ) -> None:
        self._start: int = 0
        self._turn: int = 0
        self._ticks = 0

        self._tick_limit = tick_limit
        self._turn_limit = turn_limit
        self._game_limit = game_limit

    def start(self) -> None:
        """Сбрасывает таймер."""
        self._start = int(time())
        self._turn = int(time())
        self.ticks = 0

    def tick(self) -> TimerStat:
        """Обновление таймера.

        Вызывается при каждом новом ходе.
        Добавляет счётчик ходов, текущее время хода.
        Возвращает текущую информацию о таймере.

        Предупреждения таймера выставляются в таком приоритете:
        - Игрок.
        - Счётчик.
        - Игра.
        """
        now = int(time())

        turn_delta = now - self._turn
        self._turn = now
        if self._turn_limit and turn_delta > self._turn_limit:
            alert = TimerAlert.TURN

        self._ticks += 1
        alert: TimerAlert | None = None
        if self._tick_limit and self._ticks > self._tick_limit:
            alert = TimerAlert.TICKS

        game_delta = now - self._start
        if self._game_limit and game_delta > self._game_limit:
            alert = TimerAlert.GAME

        return TimerStat(game_delta, turn_delta, self._ticks, alert)

    def stat(self) -> TimerStat:
        """возвращает статистику таймера без его обновления."""
        now = int(time())
        return TimerStat(now - self._start, now - self._turn, self._ticks, None)
