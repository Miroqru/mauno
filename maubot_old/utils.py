from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext

from maubot.mwt import MWT
from maubot.shared_vars import dispatcher, gm

TIMEOUT = 2.5

# TODO: Use aiogram user mention html
# TODO: Set default parsemode to html
def display_name(user):
    """Get the current players name including their username, if possible."""
    user_name = user.first_name
    if user.username:
        user_name += ' (@' + user.username + ')'
    return user_name

# TODO: Move to Card class
def display_color(color):
    """Convert a color code to actual color name."""
    if color == "r":
        return "❤️ Red"
    if color == "b":
        return "💙 Blue"
    if color == "g":
        return "💚 Green"
    if color == "y":
        return "💛 Yellow"

# TODO: Полностью удалить
def display_color_group(color, game):
    """Convert a color code to actual color name."""
    if color == "r":
        return "❤️ Red"
    if color == "b":
        return "💙 Blue"
    if color == "g":
        return "💚 Green"
    if color == "y":
        return "💛 Yellow"

# FIXME: Use aiogram types, mode to main bot file
def error(update: Update, context: CallbackContext):
    """Handle errors from bot."""
    logger.exception(context.error)

# TODO: Use internal aiogram methods
def send_async(bot, *args, **kwargs):
    """Send a message asynchronously."""
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT

    try:
        dispatcher.run_async(bot.sendMessage, *args, **kwargs)
    except Exception as e:
        error(None, None, e)

# TODO: Use internal aiogrma methods
def answer_async(bot, *args, **kwargs):
    """Answer an inline query asynchronously."""
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT

    try:
        dispatcher.run_async(bot.answerInlineQuery, *args, **kwargs)
    except Exception as e:
        error(None, None, e)

# TODO: Move in game class
def game_is_running(game):
    return game in gm.chatid_games.get(game.chat.id, list())

# TODO: Use aiogrma filters
def user_is_creator(user, game):
    return user.id in game.owner

def user_is_admin(user, bot, chat):
    return user.id in get_admin_ids(bot, chat.id)

def user_is_creator_or_admin(user, game, bot, chat):
    return user_is_creator(user, game) or user_is_admin(user, bot, chat)

# FIXME: Use internal aiogram mthods
# FIXME: Удалить встроеныне классы для кеширования
@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Return a list of admin IDs for a given chat.

    Results are cached for 1 hour.
    """
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
