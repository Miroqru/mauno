"""Модели базы данных.

Модели используются для хранения в базе данных.
TortoiseORM предоставляет удобный API для управления базами данных.
После модели будут конвертироваться в pydantic схемы.

Данный файл содержит все доступные модели в одном месте для удобства.
Поскольку так будет куда удобнее, чем собирать модели по всему проекту.
"""

from tortoise import Model, fields


class UserModel(Model):
    """Пользователь уно."""

    id = fields.UUIDField(primary_key=True)
    username = fields.CharField(max_length=16, unique=True)
    name = fields.CharField(max_length=64)
    password_hash = fields.TextField()
    avatar_url = fields.TextField(default="")
    gems = fields.IntField(default=100)
    play_count = fields.IntField(default=0)
    win_count = fields.IntField(default=0)
    cards_count = fields.IntField(default=0)
