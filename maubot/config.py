"""Настройки бота и Уно.

Находятся в одном месте, чтобы все обработчики могли получить доступ
к настройкам.
Загружаются один раз при запуске и больше не изменяются.
"""

from aiogram.client.default import DefaultBotProperties
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings

from mau.session import SessionManager
from maubot.events.journal import MessageJournal


class Config(BaseSettings):
    """Общие настройки для Telegram бота, касающиеся Mau.

    - telegram_token: Токен для работы Telegram бота.

    Настройки хука:
    - use_hook: Использовать webhook или long polling.
    - server_host: IP сервера дяя хука. (По умолчанию локальный)
    - server_port: На каком порту работает локальный сервер.
    - hook_root: Ссылка на сервер хука для telegram.
    - hook_root: API ручка для хука.
    - hook_secret: Дополнительный секрет для проверки событий хука.
    """

    telegram_token: SecretStr = Field()

    use_hook: bool
    server_host: str
    server_port: int
    hook_url: str
    hook_root: str
    hook_secret: str


class StickerSet(BaseModel):
    """Перечень всех стикеров, используемых во время игры."""

    normal: dict[str, str]
    not_playable: dict[str, str]


# Настройки бота по умолчанию
default = DefaultBotProperties(parse_mode="HTML")
sm: SessionManager[MessageJournal] = SessionManager()
config: Config = Config(_env_file=".env")  # type: ignore
