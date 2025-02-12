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


# TODO: Большая часть полей вообще не используется и почему не .env?
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

    stickers_path: str


try:
    with open(CONFIG_PATh) as f:
        config: Config = Config.model_validate_json(f.read())
except FileNotFoundError as e:
    logger.error(e)
    logger.info("Copy config.json.sample, then edit it")


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
