"""Настройки бота и Уно.

Находятся в одном месте, чтобы все обработчики могли получить доступ
к настройкам.
Загружаются один раз при запуске и больше не изменяются.
"""

from aiogram.client.default import DefaultBotProperties
from loguru import logger
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings

from mau.session import SessionManager
from maubot.events.journal import MessageJournal


class Config(BaseSettings):
    """Общие настройки для Telegram бота, касающиеся Uno.

    - telegram_token: Токен для работы Telegram бота.
    - stickers_path: Путь к словарю всех стикеров бота.
    - min_players: Минимальное количество игроков для начала игры.
    """

    telegram_token: SecretStr = Field()
    stickers_path: str = Field()
    min_players: int = Field()


class StickerSet(BaseModel):
    """Перечень всех стикеров, используемых во время игры."""

    normal: dict[str, str]
    not_playable: dict[str, str]


# Настройки бота по умолчанию
default = DefaultBotProperties(parse_mode="html")
sm: SessionManager[MessageJournal] = SessionManager()
config: Config = Config(_env_file=".env")  # type: ignore

try:
    with open(config.stickers_path) as f:
        stickers: StickerSet = StickerSet.model_validate_json(f.read())
except FileNotFoundError as e:
    logger.error(e)
    logger.info("First, create you own cards sticker pack.")
