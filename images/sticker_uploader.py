"""Script to upload a sticker pack to Telegram."""

import asyncio
import json
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.functions.messages import (
    GetAllStickersRequest,
    GetStickerSetRequest,
)
from telethon.tl.types import InputStickerSetID
from telethon.utils import pack_bot_file_id

from mau.deck import Deck

# Constants
# =========

# Configure paths
# Script directory (.../projects/maubot/images)
ROOT_DIR = Path(__file__).resolve().parent

# Read config fire
# Create this config file by copying the example file
with open(ROOT_DIR / "sticker_config.json", encoding="utf-8") as f:
    config = json.load(f)

NORMAL_DIR = ROOT_DIR / config["normal_dir"]
NOT_PLAYABLE_DIR = ROOT_DIR / config["not_playable_dir"]
OPTION_DIR = ROOT_DIR / config["option_dir"]

# Configure telegram client
# You must get your own api_id and api_hash from https://my.telegram.org,
# under API Development, and put them into a file called "api_auth.json"
with open(ROOT_DIR / "api_auth.json", encoding="utf-8") as f:
    api_auth = json.load(f)

# Load the session from disk, or create a new one if it doesn't exist
# Create the client and connect
client = TelegramClient(
    session=str((ROOT_DIR / "sticker_uploader.session").absolute()),
    api_id=api_auth["api_id"],
    api_hash=api_auth["api_hash"],
    receive_updates=False,
)
client.start()

# Configure cards groups
OPTIONS = [
    "bluff",
    "draw",
    "info",
    "next_turn",
]
# Колода карт
deck = Deck()
deck.fill_debug()
cards = [card.to_str() for card in deck.cards]


# Functions
# =========


def test_sticker_files() -> bool:
    """Проверяет что все файлы с изображениями существуют."""
    error_flag = False
    error_counter = 0

    for card in cards:
        card_path = NORMAL_DIR / f"{card}.png"
        unplayable_card_path = NOT_PLAYABLE_DIR / f"{card}.png"

        if card_path.exists():
            print(f"\033[92m{card_path.name}\033[0m | ", end="")
        else:
            print(f"\033[91m{card_path.name}\033[0m | ", end="")
            error_flag = True
            error_counter = 0

        if unplayable_card_path.exists():
            print(f"\033[92m{unplayable_card_path.name}\033[0m")
        else:
            print(f"\033[91m{unplayable_card_path.name}\033[0m")
            error_flag = True
            error_counter = 0

    print(f"Found {error_counter} missed cards.")
    return error_flag


async def delete_if_existing(stickers_bot: int) -> None:
    """Удаляет стикер пак, если он уже существует, затем создаёт новый."""
    sticker_sets = await client(GetAllStickersRequest(0))
    for s in sticker_sets.sets:
        if s.short_name == config["pack_name"]:
            print(f'Deleting existing sticker set "{s.short_name}" ({s.id})')
            await client.send_message(stickers_bot, "/delpack")
            await client.send_message(stickers_bot, s.short_name)
            break


async def create_sticker_set(stickers_bot: int) -> None:
    """Create a new sticker set by conversing with @Stickers."""
    await client.send_message(stickers_bot, "/newpack")
    await client.send_message(stickers_bot, config["pack_name"])


async def get_sticker_set() -> int:
    """Get the sticker set that we just created."""
    sticker_sets = await client(GetAllStickersRequest(0))
    for s in sticker_sets.sets:
        if s.short_name == config["pack_name"]:
            sticker_set_ref = s
            break
    else:
        raise Exception(f'Could not find sticker set "{config["pack_name"]}"')

    sticker_set = await client(
        GetStickerSetRequest(
            InputStickerSetID(
                id=sticker_set_ref.id, access_hash=sticker_set_ref.access_hash
            ),
            hash=0,
        )
    )
    return sticker_set


async def get_sticker_ids(sticker_set: int) -> dict[str, dict]:
    """Get the sticker file IDs of the stickers in the given sticker set."""
    sticker_iterator = iter(sticker_set.documents)
    stickers = {"normal": {}, "not_playable": {}, "options": {}}

    # Normal and not_playable sticker groups
    for group in ("normal", "not_playable"):
        for card in cards:
            stickers[group][card] = pack_bot_file_id(next(sticker_iterator))

    # Option stickers
    for option in OPTIONS:
        stickers["options"][option] = pack_bot_file_id(next(sticker_iterator))

    return stickers


async def save_sticker_ids() -> None:
    """Сохраняет словарь ID стикеров в JSON файл."""
    # Get the sticker ids
    sticker_set = await get_sticker_set()
    stickers = await get_sticker_ids(sticker_set)

    # Save the stickers to a file
    with (ROOT_DIR / f"sticker_ids_{config['pack_name']}.json").open("w") as f:
        json.dump(stickers, f, indent=4)


async def upload_sticker(stickers_bot: int, sticker_path: Path) -> None:
    """Upload a sticker to the current conversation."""
    message = await client.send_file(
        stickers_bot,
        sticker_path,
        force_document=True,
    )
    await client.send_message(stickers_bot, config["sticker_emoji"])
    return message


async def upload_sticker_group(
    stickers_bot: int, not_playable: bool = False
) -> None:
    """Отправляет группу стикеров в набор."""
    image_path = NOT_PLAYABLE_DIR if not_playable else NORMAL_DIR

    for card in cards:
        await upload_sticker(stickers_bot, image_path / f"{card}.png")
        await asyncio.sleep(1)


# Main function
# =============


async def main() -> None:
    """Простой скрипт для автоматического создания стикер пака для игры."""
    # Greeting
    stickers_bot = await client.get_entity("Stickers")
    me = await client.get_me()
    print(f"Logged in as {me.username} ({me.id})")

    ## Uncomment if you missed the prompt to
    ## add the sticker pack to your account
    await save_sticker_ids()
    return

    err = test_sticker_files()
    if err:
        raise FileNotFoundError("Not found some cards")

    # Delete the existing sticker set if it exists
    await delete_if_existing(stickers_bot)
    await asyncio.sleep(1)

    # Create a new sticker set
    await create_sticker_set(stickers_bot)

    # Upload the stickers
    # -------------------

    await upload_sticker_group(stickers_bot, not_playable=False)
    await upload_sticker_group(stickers_bot, not_playable=True)

    # Upload options cards
    for option in OPTIONS:
        await upload_sticker(stickers_bot, OPTION_DIR / f"{option}.png")
        await asyncio.sleep(1)

    await client.send_message(stickers_bot, "/publish")
    await client.send_message(stickers_bot, "/skip")
    await client.send_message(stickers_bot, config["pack_name"])

    # Wait for the user to add the sticker pack to their account
    print("Please add the sticker pack to your account by clicking the link!")
    print(f"https://t.me/addstickers/{config['pack_name']}")
    await asyncio.sleep(10)

    # Save the sticker IDs to a file
    await save_sticker_ids()


# Start script
# ============

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
