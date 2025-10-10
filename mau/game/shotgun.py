"""Игровой револьвер."""

from random import randint


class Shotgun:
    """Револьвер.

    8 патронов, один из них заряжен.
    Используется в специальном режиме игры.
    """

    def __init__(self) -> None:
        self._cur = 0
        self._lose = randint(1, 8)

    @property
    def cur(self) -> int:
        """Возвращает число выстрелов револьвера."""
        return self._cur

    def shot(self) -> bool:
        """Выстреливает из револьвера."""
        self._cur += 1
        return self._cur >= self._lose
