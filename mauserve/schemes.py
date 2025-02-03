"""Список глобальных схем.

Схемы используются для валидации данных между клиентом и сервером.
Все схемы автоматически запаковываются и распаковываются из JSON.

Данный файл предоставляет общие схемы, которые могут быть доступны
из всех компонентов сервера.
Модели, специфичные для конкретных компонентов можно найти в директории
компонентов.
"""

from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from mauserve.models import UserModel

# Конвертированные модели
# =======================

# Чтобы корректно отображались зависимые модели
# Как например пользователи в модели подсписок
Tortoise.init_models(["mauserve.models"], "models")

# Данные модели были конвертированные из TortoiseORM и доступны всем.
UserData = pydantic_model_creator(
    UserModel, name="UserData", exclude=["id", "password_hash"]
)
