"""Получает игровой контекст."""

from fastapi import Depends, HTTPException

from mauserve.config import sm, stm
from mauserve.models import RoomModel, UserModel
from mauserve.schemes.game import GameContext


async def get_context(user: UserModel = Depends(stm.read_token)) -> GameContext:
    """Получает игровой контекст пользователя.

    Контекст хранит в себе исчерпывающую информацию о состоянии игры.
    Актуальная информация об активном игроке.
    В какой комнате сейчас находится игрок.
    Если игрок не находится в комнате, вернётся ошибка.
    Также включат информацию об игре внутри комнаты и пользователя
    как игрока.
    """
    room = (
        await RoomModel.filter(players=user)
        .exclude(status="ended")
        .get_or_none()
        .prefetch_related("players")
    )
    if room is None:
        raise HTTPException(404, "user not in room, to join room game")

    game = sm.games.get(str(room.id))
    if game is not None:
        player = game.get_player(user.username)
    else:
        player = None

    return GameContext(
        user=user,
        room=room,
        game=game,
        player=player,
    )
