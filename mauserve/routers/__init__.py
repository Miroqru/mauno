"""Хранит в себе все публичные роутеры сервера."""

from mauserve.routers import games, leaaderboard, roomlist, users

ROUTERS = (roomlist.router, leaaderboard.router, games.router, users.router)

__all__ = ("ROUTERS",)
