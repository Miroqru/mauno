"""Хранилище игровых сессий."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

_V = TypeVar("_V")


class BaseStorage(ABC, Generic[_V]):
    """Базовое хранилище сессий.

    Описывает интерфейс для работы с хранилищем сессий.
    Позволяет сохранять состояние игр в памяти.
    """

    @abstractmethod
    def add(self, key: str, value: _V) -> None:
        """Добавляет новый элемент в хранилище."""
        pass

    @abstractmethod
    def remove(self, key: str) -> _V:
        """Удаляет игрока из хранилища."""
        pass

    @abstractmethod
    def get(self, key: str) -> _V:
        """Возвращает значение из хранилища."""
        pass


class MemoryStorage(BaseStorage, Generic[_V]):
    """Хранилище сессий в памяти.

    Самые простой вид хранилища.
    Сохраняет состояние в оперативной памяти.
    Сессии будут очищены после перезапуска программы.

    У каждого игрока может быть только одна активная игра.
    """

    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[str, _V] = {}

    def add(self, key: str, value: _V) -> None:
        """Добавляет новый элемент в хранилище."""
        self._storage[key] = value

    def remove(self, key: str) -> _V:
        """Удаляет игрока из хранилища."""
        return self._storage.pop(key)

    def get(self, key: str) -> _V:
        """Возвращает значение из хранилища."""
        return self._storage[key]
