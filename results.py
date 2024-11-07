"""Defines helper functions to build the inline result list."""

from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import InlineQueryResultCachedSticker as Sticker

import card as c
from internationalization import _, __
from utils import display_color, display_color_group, display_name


def add_choose_color(results, game):
    """Add choose color options."""
    for color in c.COLORS:
        results.append(
            InlineQueryResultArticle(
                id=color,
                title=_("Choose Color"),
                description=display_color(color),
                input_message_content=
                InputTextMessageContent(display_color_group(color, game))
            )
        )

def add_other_cards(player, results, game):
    """Add hand cards when choosing colors."""
    results.append(
        InlineQueryResultArticle(
            "hand",
            title=_("Card (tap for game state):",
                    "Cards (tap for game state):",
                    len(player.cards)),
            description=', '.join([repr(card) for card in player.cards]),
            input_message_content=game_info(game)
        )
    )


def player_list(game):
    """Generate list of player strings."""
    return [_("{name} ({number} card)",
              "{name} ({number} cards)",
              len(player.cards))
            .format(name=player.user.first_name, number=len(player.cards))
            for player in game.players]


def add_no_game(results):
    """Add text result if user is not playing."""
    results.append(
        InlineQueryResultArticle(
            "nogame",
            title=_("You are not playing"),
            input_message_content=
            InputTextMessageContent(_('Not playing right now. Use /new to '
                                      'start a game or /join to join the '
                                      'current game in this group'))
        )
    )

def add_not_started(results):
    """Add text result if the game has not yet started."""
    results.append(
        InlineQueryResultArticle(
            "nogame",
            title=_("The game wasn't started yet"),
            input_message_content=
            InputTextMessageContent(_('Start the game with /start'))
        )
    )


def add_mode_classic(results):
    """Change mode to classic."""
    results.append(
        InlineQueryResultArticle(
            "mode_classic",
            title=_("🎻 Classic mode"),
            input_message_content=
            InputTextMessageContent(_('Classic 🎻'))
        )
    )

def add_mode_fast(results):
    """Change mode to fast."""
    results.append(
        InlineQueryResultArticle(
            "mode_fast",
            title=_("🚀 Sanic mode"),
            input_message_content=
            InputTextMessageContent(_('Gotta go fast! 🚀'))
        )
    )

def add_mode_wild(results):
    """Change mode to classic."""
    results.append(
        InlineQueryResultArticle(
            "mode_wild",
            title=_("🐉 Wild mode"),
            input_message_content=
            InputTextMessageContent(_('Into the Wild~ 🐉'))
        )
    )

def add_mode_text(results):
    """Change mode to text."""
    results.append(
        InlineQueryResultArticle(
            "mode_text",
            title=_("✍️ Text mode"),
            input_message_content=
            InputTextMessageContent(_('Text ✍️'))
        )
    )


def add_draw(player, results):
    """Add option to draw."""
    n = player.game.draw_counter or 1
    results.append(
        Sticker(
            "draw", sticker_file_id=c.STICKERS['option_draw'],
            input_message_content=
            InputTextMessageContent(__('Drawing {number} card',
                                       'Drawing {number} cards', n,
                                       multi=player.game.translate)
                                    .format(number=n))
        )
    )

def add_gameinfo(game, results):
    """Add option to show game info."""
    results.append(
        Sticker(
            "gameinfo",
            sticker_file_id=c.STICKERS['option_info'],
            input_message_content=game_info(game)
        )
    )

def add_pass(results, game):
    """Add option to pass."""
    results.append(
        Sticker(
            "pass", sticker_file_id=c.STICKERS['option_pass'],
            input_message_content=InputTextMessageContent(
                __('Pass', multi=game.translate)
            )
        )
    )

def add_call_bluff(results, game):
    """Add option to call a bluff."""
    results.append(
        Sticker(
            "call_bluff",
            sticker_file_id=c.STICKERS['option_bluff'],
            input_message_content=
            InputTextMessageContent(__("I'm calling your bluff!",
                                       multi=game.translate))
        )
    )

def add_card(game, card, results, can_play):
    """Add an option that represents a card."""
    if can_play:
        if game.mode != "text":
            results.append(
                Sticker(str(card), sticker_file_id=c.STICKERS[str(card)])
        )
        if game.mode == "text":
            results.append(
                Sticker(str(card), sticker_file_id=c.STICKERS[str(card)], input_message_content=InputTextMessageContent("Card Played: {card}".format(card=repr(card).replace('Draw Four', '+4').replace('Draw', '+2').replace('Colorchooser', 'Color Chooser')))
        ))
    else:
        results.append(
            Sticker(str(uuid4()), sticker_file_id=c.STICKERS_GREY[str(card)],
                    input_message_content=game_info(game))
        )

def game_info(game):
    players = player_list(game)
    return InputTextMessageContent(
        _("Current player: {name}")
        .format(name=display_name(game.current_player.user)) +
        "\n" +
        _("Last card: {card}").format(card=repr(game.last_card)) +
        "\n" +
        _("Player: {player_list}",
          "Players: {player_list}",
          len(players))
        .format(player_list=" -> ".join(players))
    )
