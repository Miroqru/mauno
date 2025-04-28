"""Инициализация всех обработчиков.

Весь функционал бота был поделён на обработчики для большей гибкости.
"""

from maubot.handlers import deck, player, session, simple_commands, turn

# Список всех работающих роутеров
ROUTERS = (
    deck.router,
    player.router,
    session.router,
    simple_commands.router,
    turn.router,
)

__all__ = ("ROUTERS",)
