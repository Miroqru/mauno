"""Ручки пользователей.

Позволяет взаимодействовать с пользователями платформы.
Регистрировать новых пользователей.
Обновлять данные пользователей.
Работать с токенами для авторизации.
Проверять платную подписку пользователя.
Управлять подписчиками.
"""

from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from tortoise.exceptions import IntegrityError

from mauserve.config import stm
from mauserve.models import UserModel
from mauserve.schemes import UserData
from mauserve.users.schemes import (
    ChangePasswordDataIn,
    EditUserDataIn,
    UserDataIn,
)

router = APIRouter(prefix="/users", tags=["users"])

# Список пользователей
# ====================


@router.get("/")
async def get_users() -> list[UserData]:
    """Получает всех пользователей из базы данных."""
    return await UserData.from_queryset(UserModel.all())


# Регистрация пользователя
# ========================


@router.post("/", response_model=UserData)
async def register_user(
    user: Annotated[UserDataIn, "Данные для регистрации"],
) -> UserData:
    """Регистрирует нового пользователя."""
    try:
        new_user = await UserModel.create(
            username=user.username,
            name=user.username,
            password_hash=str(
                bcrypt.hashpw(bytes(user.password, "utf-8"), bcrypt.gensalt()),
                "utf-8",
            ),
        )
    except IntegrityError as e:
        logger.exception(e)
        raise HTTPException(409, "Incorrect username")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Error while create new user")

    return await UserData.from_tortoise_orm(new_user)


@router.post("/change-password")
async def change_my_password(
    password_data: ChangePasswordDataIn,
    user: UserModel = Depends(stm.read_token),
) -> UserData:
    """Процедура смены пароля пользователя.

    Для смены пароля требуется подтвердить личность при помощи токена.
    Также требуется сопоставить данные со старым паролем.
    """
    if not bcrypt.checkpw(
        bytes(password_data.old_password, "utf-8"),
        bytes(user.password_hash, "utf-8"),
    ):
        raise HTTPException(401, "Invalid password")
    user.password_hash = str(
        bcrypt.hashpw(
            bytes(password_data.new_password, "utf-8"), bcrypt.gensalt()
        ),
        "utf-8",
    )
    await user.save()
    return await UserData.from_tortoise_orm(user)


@router.post("/login")
async def login_user(
    userdata: Annotated[UserDataIn, "Данные для входа"],
) -> dict[str, str]:
    """Получает новый токен для пользователя."""
    user = await UserModel.get_or_none(username=userdata.username)
    if user is None:
        raise HTTPException(401, "Incorrect user or password")

    if bcrypt.checkpw(
        bytes(userdata.password, "utf-8"), bytes(user.password_hash, "utf-8")
    ):
        return {"status": "ok", "token": stm.new_token(user)}
    else:
        raise HTTPException(401, "Incorrect user or password")


@router.get("/me")
async def get_my_profile(user: UserModel = Depends(stm.read_token)) -> UserData:
    """Получает ваш профиль.

    неплохой способ чтобы проверить работу токена.
    """
    return await UserData.from_tortoise_orm(user)


@router.put("/")
async def edit_my_profile(
    edit_user: EditUserDataIn, user: UserModel = Depends(stm.read_token)
) -> UserData:
    """Изменяет основные данные пользователя."""
    user.update_from_dict(edit_user.model_dump(exclude_unset=True))
    await user.save()
    return await UserData.from_tortoise_orm(user)


@router.get("/{username}")
async def get_user_by_username(username: str) -> UserData:
    """Получает информацию о пользователе по его ID.

    Если такого пользователя не существует, то вернёт 404.
    """
    if len(username) > 16:  # noqa: PLR2004
        raise HTTPException(404, "User not found")

    user = await UserModel.get_or_none(username=username)
    if user is None:
        raise HTTPException(404, "User not found")

    return await UserData.from_tortoise_orm(user)
