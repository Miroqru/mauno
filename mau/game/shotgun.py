"""Компонент револьвера."""

from random import randint


class Shotgun:
    """Револьвер.

    6 патронов, один из них заряжен.
    Используется в некоторых режимах игры.
    """

    def __init__(self) -> None:
        self._cur = 0
        self._lose = 0

    @property
    def cur(self) -> int:
        """Возвращает текущей число выстрелов револьвера."""
        return self._cur

    def reset(self) -> None:
        """Перезаряжает револьвер."""
        self._cur = 0
        self._lose = randint(1, 8)

    def shot(self) -> bool:
        """Выстреливает из револьвера."""
        self._cur += 1
        return self._cur >= self._lose
