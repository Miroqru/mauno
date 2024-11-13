"""Defines helper functions to build the inline result list."""

from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import InlineQueryResultCachedSticker as Sticker

import maubot.uno.card as c
from maubot.utils import display_color, display_color_group, display_name


def add_choose_color(results, game):
    """Add choose color options."""
    for color in c.COLORS:
        results.append(InlineQueryResultArticle(
            id=color,
            title="Choose Color",
            description=display_color(color),
            input_message_content=InputTextMessageContent(
                display_color_group(color, game)
            )
        ))

def add_other_cards(player, results, game):
    """Add hand cards when choosing colors."""
    results.append(InlineQueryResultArticle(
        "hand",
        title="Cards (tap for game state):",
        description=", ".join([repr(card) for card in player.cards]),
        input_message_content=game_info(game),
    ))

def player_list(game):
    """Generate list of player strings."""
    return [
        f"{player.user.first_name} ({len(player.cards)} cards)"
        for player in game.players
    ]

def add_draw(player, results):
    """Add option to draw."""
    n = player.game.draw_counter or 1
    results.append(Sticker("draw",
        sticker_file_id=c.STICKERS["option_draw"],
        input_message_content=InputTextMessageContent(f"Drawing {n} cards",)
    ))

def add_gameinfo(game, results):
    """Add option to show game info."""
    results.append(Sticker("gameinfo",
        sticker_file_id=c.STICKERS["option_info"],
        input_message_content=game_info(game),
    ))

def add_pass(results, game):
    """Add option to pass."""
    results.append(Sticker("pass",
        sticker_file_id=c.STICKERS["option_pass"],
        input_message_content=InputTextMessageContent("Pass")
    ))

def add_call_bluff(results, game):
    """Add option to call a bluff."""
    results.append(Sticker("call_bluff",
        sticker_file_id=c.STICKERS["option_bluff"],
        input_message_content=InputTextMessageContent(
            "I'm calling your bluff!"
        )
    ))

def add_card(game, card, results, can_play):
    """Add an option that represents a card."""
    if not can_play:
        return results.append(Sticker(str(uuid4()),
            sticker_file_id=c.STICKERS_GREY[str(card)],
            input_message_content=game_info(game),
        ))

    if game.mode != "text":
        return results.append(Sticker(str(card),
            sticker_file_id=c.STICKERS[str(card)])
        )

    results.append(Sticker(str(card),
        sticker_file_id=c.STICKERS[str(card)],
        input_message_content=InputTextMessageContent(f"Card Played: {card}")
    ))

def game_info(game):
    return InputTextMessageContent((
        f"Current player: {display_name(game.current_player.user)}\n"
        f"Last card: {game.last_card}\n"
        f"Players: {' -> '.join(player_list(game))}"
    ))
