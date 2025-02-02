"""Модели базы данных.

Модели используются для хранения в базе данных.
TortoiseORM предоставляет удобный API для управления базами данных.
После модели будут конвертироваться в pydantic схемы.

Данный файл содержит все доступные модели в одном месте для удобства.
Поскольку так будет куда удобнее, чем собирать модели по всему проекту.
"""

import uuid

from tortoise import Model, fields


class UserMode(Model):
    """Пользователь уно."""

    id = fields.TextField(primary_key=True, default=uuid.uuid4())
    username = fields.CharField(max_length=16)
    name = fields.CharField(max_length=64)
    password_hash = fields.TextField()
    avatar_url = fields.TextField()
    gems = fields.IntField(default=100)
    play_count = fields.IntField(default=0)
    win_count = fields.IntField(default=0)
    cards_count = fields.IntField(default=0)
