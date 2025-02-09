"""Схемы, характерные для пользователя."""

from pydantic import BaseModel, Field


class UserDataIn(BaseModel):
    """Данные для регистрации/входа нового пользователя.

    Включает необходимый минимум при создании нового пользователя.
    Поля не указанные в данной схеме пользователь сможет заполнить
    самостоятельно после в разделе профиля.
    """

    username: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=8)


class ChangePasswordDataIn(BaseModel):
    """Схема смены пароля пользователя."""

    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class EditUserDataIn(BaseModel):
    """Изменение данных пользователя.

    Данная схема описывает как пользователь может изменять свою
    персональную информацию.
    Это касается только основных полей.
    Для смены электронной почты или пароля, будет происходить
    отдельная процедура.
    """

    username: str = Field(default=None, max_length=16)
    name: str = Field(default=None, min_length=4, max_length=64)
    avatar_url: str | None = None
