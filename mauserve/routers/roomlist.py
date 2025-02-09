"""Работа со списком комнат."""

import random

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from tortoise.queryset import QuerySet

from mauserve.config import redis, stm
from mauserve.mau.rules import RULES
from mauserve.models import RoomModel, UserModel
from mauserve.schemes.db import RoomData
from mauserve.schemes.roomlist import RoomDataIn, RoomMode, RoomModeIn

router = APIRouter(prefix="/rooms", tags=["room list"])


# получение информации о комнатах
# ===============================


@router.get("/")
async def get_public_rooms(
    order_by: str | None = "create_time", invert: bool | None = False
) -> list[RoomData]:
    """Получает все доступные открытые комнаты."""
    return await RoomData.from_queryset(
        RoomModel.filter(private=False)
        .exclude(status="ended")
        .order_by("-" + order_by if not invert else order_by)
    )


@router.get("/active")
async def get_active_user_room(
    user: UserModel = Depends(stm.read_token),
) -> RoomData:
    """Получает комнату, в которой сейчас находится пользователь."""
    active_room: QuerySet[RoomModel] = (
        await RoomModel.filter(players=user)
        .exclude(status="ended")
        .get_or_none()
    )

    if active_room is None:
        raise HTTPException(404, "User is now no in room")

    return await RoomData.from_tortoise_orm(active_room)


@router.get("/random")
async def get_random_room() -> RoomData:
    """Получает случайную доступную комнату."""
    rooms: QuerySet[RoomModel] = await RoomModel.filter(private=False).exclude(
        status="ended"
    )
    if len(rooms) == 0:
        raise HTTPException(404, "No open rooms to join")
    random_room = rooms[random.randint(0, len(rooms))]
    return await RoomData.from_tortoise_orm(random_room)


@router.get("/{room_id}")
async def get_room_info(room_id: str) -> RoomData:
    """Получает информацию о комнате по её ID."""
    room = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    return await RoomData.from_tortoise_orm(room)


# Управление комнатой
# ===================


@router.post("/")
async def create_new_room(
    user: UserModel = Depends(stm.read_token),
) -> RoomData:
    """Создаёт новую пользовательскую комнату."""
    current_room = await RoomModel.exclude(status="ended").get_or_none(
        players=user.id
    )
    if current_room is not None:
        raise HTTPException(409, "User already in room")

    room = await RoomModel.create(
        name=f"комната {user.name}",
        owner_id=user.id,
    )
    await room.players.add(user)
    return await RoomData.from_tortoise_orm(room)


@router.put("/{room_id}")
async def update_room(
    room_id: str,
    room_data: RoomDataIn,
    user: UserModel = Depends(stm.read_token),
) -> RoomData:
    """Обновляет информацию о комнате."""
    room: RoomModel = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    if room.owner_id != user.id:
        raise HTTPException(401, "User is not room owner")

    logger.debug(room_data)
    await room.update_from_dict(room_data.model_dump(exclude_unset=True))
    await room.save()

    return await RoomData.from_tortoise_orm(room)


@router.delete("/{room_id}")
async def delete_room(
    room_id: str,
    user: UserModel = Depends(stm.read_token),
) -> dict:
    """Принудительно удаляет комнату."""
    room: RoomModel = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    if room.owner_id != user.id:
        raise HTTPException(401, "User is not room owner")

    await room.delete()
    return {"ok": True, "room_id": room_id, "user": user}


# Игровые режимы
# ==============


# TODO: А как режимы делать тут
@router.get("/{room_id}/modes")
async def get_room_modes(room_id: str) -> list[RoomMode]:
    """Получает информацию о выбранных режимах."""
    active_modes = await redis.lrange(f"room:{room_id}:rules", 0, -1)
    res = []
    for rule in RULES:
        res.append(
            RoomMode(
                key=rule.key, name=rule.name, status=rule.key in active_modes
            )
        )
    return res


@router.put("/{room_id}/modes")
async def update_room_modes(
    room_id: str,
    rules: RoomModeIn,
    user: UserModel = Depends(stm.read_token),
) -> list[RoomMode]:
    """Обновляет список игровых режимов для комнаты."""
    room: RoomModel = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    if room.owner_id != user.id:
        raise HTTPException(401, "User is not room owner")

    await redis.delete(f"room:{room_id}:rules")
    await redis.rpush(f"room:{room_id}:rules", *rules.rules)
    res = []
    for rule in RULES:
        res.append(
            RoomMode(
                key=rule.name, name=rule.name, status=rule.key in rules.rules
            )
        )
    return res


# Участники комнаты
# =================


@router.post("/{room_id}/join")
async def join_in_room(
    room_id: str,
    user: UserModel = Depends(stm.read_token),
) -> RoomData:
    """Добавляет пользователя в комнату."""
    current_room = await RoomModel.exclude(status="ended").get_or_none(
        players=user.id
    )
    if current_room is not None:
        raise HTTPException(409, "User already join another room")

    room: RoomModel = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")

    room_user = await room.players.filter(id=user.id).first()
    if room_user is not None:
        raise HTTPException(409, "User already join this room")

    if room.gems > user.gems:
        raise HTTPException(403, "Not enough gems to join room")

    await room.players.add(user)
    return await RoomData.from_tortoise_orm(room)


@router.post("/{room_id}/kick/{username}")
async def kick_user_from_room(
    room_id: str,
    username: str,
    user: UserModel = Depends(stm.read_token),
) -> RoomData:
    """Выгоняет пользователя из комнату."""
    room: RoomModel = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    if room.owner_id != user.id:
        raise HTTPException(401, "User is not room owner")
    kick_user = await room.players.filter(username=username).first()
    if kick_user is None:
        raise HTTPException(404, "User to kick not found in room")
    await room.players.remove(kick_user)
    return await RoomData.from_tortoise_orm(room)


@router.post("/{room_id}/owner/{username}")
async def set_user_room_owner(
    room_id: str,
    username: str,
    user: UserModel = Depends(stm.read_token),
) -> RoomData:
    """Назначает пользователя владельцем комнаты."""
    room: RoomModel = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    if room.owner_id != user.id:
        raise HTTPException(401, "User is not room owner")
    new_owner_user = await room.players.filter(username=username).first()
    if new_owner_user is None:
        raise HTTPException(404, "User to set owner not found in room")
    room.owner = new_owner_user
    return await RoomData.from_tortoise_orm(room)


@router.post("/{room_id}/leave")
async def leave_from_room(
    room_id: str,
    user: UserModel = Depends(stm.read_token),
) -> RoomData:
    """Выход из комнаты."""
    room: RoomModel = await RoomModel.get_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    room_user = await room.players.filter(id=user.id).first()
    if room_user is None:
        raise HTTPException(409, "User not found in this room")

    # Когда выходит создатель, вся комната завершается
    if user.id == room.owner_id:
        room.status = "ended"
        await room.save()
    else:
        await room.players.remove(room_user)
    return await RoomData.from_tortoise_orm(room)


@router.post("/{room_id}/start")
async def start_new_game(room_id: str) -> str:
    """Начало новой игры."""
    # TODO: Нормальный выхлоп тут бы нужен
    return "New game!"
