"""Инициализация всех роутеров.

Весь функционал бота был поделён на различные обработчики для
большей гибкости.
"""

from maubot.handlers import deck, player, session, simple_commands, turn

# Список всех работающих роутеров
# Роутеры из этого списка будут включены в диспетчер бота
ROUTERS = (
    # Основная информация о пользователе
    deck.router,
    player.router,
    session.router,
    simple_commands.router,
    turn.router,
)

__all__ = ("ROUTERS",)
