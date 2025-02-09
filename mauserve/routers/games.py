"""Обработка игры."""

from enum import StrEnum

from fastapi import APIRouter, Depends, HTTPException

from mauserve.config import stm
from mauserve.models import RoomModel, UserModel
from mauserve.schemes.db import RoomData, UserData

router = APIRouter(prefix="/game", tags=["games"])


async def active_room(user: UserModel = Depends(stm.read_token)):
    return (
        await RoomModel.filter(players=user)
        .exclude(status="ended")
        .get_or_none()
    )


@router.get("/")
async def get_active_game(room: RoomModel = Depends(active_room)):
    """Получает активную комнату пользователя."""
    if room is None:
        HTTPException(404, "User not in room")

    return RoomData.from_tortoise_orm(room)
