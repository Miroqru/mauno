"""Настройки бота и Уно.

Находятся в одном месте, чтобы все обработчики могли получить доступ
к настройкам.
Загружаются один раз при запуске и больше не изменяются.
"""

from pathlib import Path

from aiogram.client.default import DefaultBotProperties
from loguru import logger
from pydantic import BaseModel, SecretStr

# Общие настройки бота
# ====================

CONFIG_PATh = Path("config.json")

class Config(BaseModel):
    """Общие настройки для Telegram бота, касающиеся Uno."""

    token: SecretStr
    admin_list: list[int]
    db_url: str = "sqlite://uno.sqlite"
    open_lobby: bool = True
    default_gamemode: str = "classic"
    waiting_time: int = 120
    time_removal_after_skip: int = 20
    min_fast_turn_time: int = 15
    min_players: int = 2

try:
    with open(CONFIG_PATh) as f:
        config: Config = Config.model_validate_json(f.read())
except FileNotFoundError as e:
    logger.error(e)
    logger.info("Copy config.json.sample, then edit it")


# Параметры по умолчанию для бота aiogram
# =======================================

# Настройки бота по умолчанию
default = DefaultBotProperties(
    parse_mode="html"
)
