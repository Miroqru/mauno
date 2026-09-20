"""Пере используемые типы в движке."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.game.player import Player
    from mau.rules import GameRules

type PlayerID = str
"""Уникальный идентификатор игрока."""

type PlayerOrID = "Player | PlayerID"
"""Пользователь или его идентификатор."""

type RoomID = str
"""Уникальный идентификатор комнаты."""

type Rule = "GameRules | int"
"""Игровое правило или соответствующий ему битовый флаг."""
