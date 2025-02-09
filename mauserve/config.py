"""Общие настройки сервера.

Здесь будут храниться необходимые для запуска приложения настройки.
Такие как url подключения к базе данных или секретные ключи для токенов.
Данные настройки будут храниться как переменные окружения в .env файле.
"""

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from redis.asyncio.client import Redis

from mauserve.token import SimpleTokenManager


class Config(BaseSettings):
    """Хранит все настройки сервера.

    :param jwt_key: Ключ для генерации токенов.
    :type jwt_key: SecretStr
    :param db_url: Путь к основной базе данных для TortoiseORM.
    :type db_path: SecretStr
    :param test_db_url: Путь к тестовой базе данных для TortoiseORM.
    :type test_db_url: SecretStr
    :param debug: Отладочный режим работы без сохранения данных.
    :type debug: bool
    """

    jwt_key: str
    db_url: PostgresDsn
    test_db_url: str
    redis_url: str
    debug: bool


# Создаём экземпляр настроек
config = Config(_env_file=".env")

stm = SimpleTokenManager(config.jwt_key, ttl=86_400)
redis = Redis.from_url(
    config.redis_url, encoding="utf-8", decode_responses=True
)
