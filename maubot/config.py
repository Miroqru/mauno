"""Настройки бота и Уно.

Находятся в одном месте, чтобы все обработчики могли получить доступ
к настройкам.
Загружаются один раз при запуске и больше не изменяются.
"""

from aiogram.client.default import DefaultBotProperties
from loguru import logger
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from mau.session import SessionManager


class Config(BaseSettings):
    """Общие настройки для Telegram бота, касающиеся Uno.

    - telegram_token: Токен для работы Telegram бота.
    - stickers_path: Путь к словарю всех стикеров бота.
    - min_players: Минимальное количество игроков для начала игры.
    """

    telegram_token: SecretStr = Field()
    stickers_path: str = Field()
    min_players: int = Field()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


config: Config = Config()  # type: ignore

# Настройка стикеров
# ==================


class OptionStickersID(BaseModel):
    """Стикеры для специальных действий во время игры.

    - bluff: обвинить другого игрока во лжи, когда он разыграл +4
    - draw: Взять карту из колоды.
    - info: Посмотреть текущий статус игры.
    - next_turn: Передать ход следующему игроку / пропустить.
    """

    bluff: str
    draw: str
    info: str
    next_turn: str


class StickerSet(BaseModel):
    """Перечень всех стикеров, используемых во время игры."""

    normal: dict[str, str]
    not_playable: dict[str, str]
    options: OptionStickersID


try:
    with open(config.stickers_path) as f:
        stickers: StickerSet = StickerSet.model_validate_json(f.read())
except FileNotFoundError as e:
    logger.error(e)
    logger.info("First, create you own cards sticker pack.")


# Параметры по умолчанию для бота aiogram
# =======================================

# Настройки бота по умолчанию
default = DefaultBotProperties(parse_mode="html")
sm = SessionManager()
