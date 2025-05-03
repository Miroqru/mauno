"""Простой скрипт для загрузки директории изображений как набор стикеров.

Version: v2.0
Author: Milinuri Nirvalen
"""

import argparse
import asyncio
import json
from pathlib import Path

import aiofiles
from telethon import TelegramClient
from telethon.tl.functions.messages import (
    GetAllStickersRequest,
    GetStickerSetRequest,
)
from telethon.tl.types import InputStickerSetID
from telethon.utils import pack_bot_file_id

from mau.deck_generator import DeckGenerator

# Функции для проверки
# ====================

# Список опций, которые будут использоваться
OPTIONS = [
    "bluff",
    "draw",
    "info",
    "next_turn",
]


# Работа с ботом
# ==============


async def delete_if_existing(
    stickers_bot: int, client: TelegramClient, name: str
) -> None:
    """Удаляет стикер пак, если он уже существует, затем создаёт новый."""
    stickers = await client(GetAllStickersRequest(0))
    for s in stickers.sets:
        if s.short_name == name:
            print(f'Delete existing set "{s.short_name}" ({s.id})')
            await client.send_message(stickers_bot, "/delpack")
            await client.send_message(stickers_bot, s.short_name)
            break


async def get_sticker_set(client: TelegramClient, name: str) -> int:
    """Get the sticker set that we just created."""
    sticker_set_ref = None
    stickers = await client(GetAllStickersRequest(0))
    for s in stickers.sets:
        if s.short_name == name:
            sticker_set_ref = s
            break

    if sticker_set_ref is None:
        raise Exception(f'Could not find sticker set "{name}"')

    sticker_set = await client(
        GetStickerSetRequest(
            InputStickerSetID(
                id=sticker_set_ref.id, access_hash=sticker_set_ref.access_hash
            ),
            hash=0,
        )
    )
    return sticker_set


async def get_sticker_ids(sticker_set: int, items: list[str]) -> dict[str, str]:
    """Get the sticker file IDs of the stickers in the given sticker set."""
    sticker_iterator = iter(sticker_set.documents)
    sticker_ids = {}

    # Normal and not_playable sticker groups
    for item in items:
        sticker_ids[item] = pack_bot_file_id(next(sticker_iterator))

    return sticker_ids


async def upload_sticker(
    stickers_bot: int, client: TelegramClient, sticker_path: Path
) -> None:
    """Upload a sticker to the current conversation."""
    message = await client.send_file(
        stickers_bot,
        sticker_path,
        force_document=True,
    )
    await client.send_message(stickers_bot, "🎮")
    return message


# Работает со стикер паком
# ========================


async def save_sticker_ids(
    client: TelegramClient, name: str, items: list[str]
) -> None:
    """Сохраняет словарь ID стикеров в JSON файл."""
    async with aiofiles.open(Path(f"sticker_ids_{name}.json"), "w") as f:
        await f.write(
            json.dumps(
                await get_sticker_ids(
                    await get_sticker_set(client, name), items
                ),
                indent=4,
            )
        )


def validate_items(path: Path, items: list[str]) -> bool:
    """Проверяет что все файлы с изображениями существуют."""
    error_flag = False
    error_counter = 0

    for item in items:
        item_path = path / Path(f"{item}.png")

        if item_path.exists():
            print(f"\033[92m{item}\033[0m", end=" ")
        else:
            print(f"\033[91m{item}\033[0m", end=" ")
            error_flag = True
            error_counter += 1

    print(f"\nFound {error_counter} missed cards.")
    return error_flag


async def upload_items(
    sticker_bot: int, path: Path, items: list[str], client: TelegramClient
) -> None:
    """Загружает файлы из стикеров."""
    for item in items:
        item_path = path / Path(f"{item}.png")
        await upload_sticker(sticker_bot, client, item_path)
        await asyncio.sleep(1)


async def main() -> None:
    """Главная функция скрипта.

    - Разбирает аргументы командной строки.
    - удаляет старый стикер пак.
    - проверяет наличие всех файлов.
    - Загружает файлы как стикер пак.
    - Сохраняет ID стикеров в файл.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Путь к стикер паку")
    parser.add_argument("name", help="Название стикер пака")
    parser.add_argument(
        "--auth",
        "-a",
        help="Путь к авторизации",
        default=Path("config.json"),
        type=Path,
    )
    parser.add_argument(
        "-o",
        "--options",
        action="store_true",
        help="Загрузить стикер пак опций",
    )
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Сохранить список ID стикеров без загрузки",
    )
    args = parser.parse_args()

    async with aiofiles.open(args.auth, encoding="utf-8") as f:
        config = json.loads(await f.read())

    client = TelegramClient(
        session="sticker_uploader.session",
        api_id=config["api_id"],
        api_hash=config["api_hash"],
        receive_updates=False,
    )

    await client.start()
    stickers_bot = await client.get_entity("Stickers")
    me = await client.get_me()
    print(f"Logged in as {me.username} ({me.id})")

    if args.options:
        items = OPTIONS
    else:
        # Жёстко получаем все доступные карты к колоде
        deck = DeckGenerator.from_preset("single").get_deck()
        items = [card.to_str() for card in deck.cards]

    # Только сохраняем
    validate_err = validate_items(args.path, items)

    if args.save:
        await save_sticker_ids(client, args.name, items)

    elif not validate_err:
        # Delete the existing sticker set if it exists
        await delete_if_existing(stickers_bot, client, args.name)
        await asyncio.sleep(1)

        # Create a new sticker set
        await client.send_message(stickers_bot, "/newpack")
        await client.send_message(stickers_bot, args.name)

        await upload_items(stickers_bot, args.path, items, client)

        await client.send_message(stickers_bot, "/publish")
        await client.send_message(stickers_bot, "/skip")
        await client.send_message(stickers_bot, args.name)

        print(
            "Please add the sticker pack to your account by clicking the link!"
        )
        print(f"https://t.me/addstickers/{args.name}")
        await asyncio.sleep(10)

        await save_sticker_ids(client, args.name, items)


if __name__ == "__main__":
    asyncio.run(main())
