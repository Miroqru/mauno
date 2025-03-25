"""Хранит в себе все публичные маршруты сервера."""

from mauserve.routers import game, leaaderboard, roomlist, users

ROUTERS = (roomlist.router, leaaderboard.router, game.router, users.router)

__all__ = ("ROUTERS",)
