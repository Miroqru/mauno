import logging

from telegram import Update
from telegram.ext import CallbackContext

from maubot.internationalization import _, __
from maubot.mwt import MWT
from maubot.shared_vars import dispatcher, gm

logger = logging.getLogger(__name__)

TIMEOUT = 2.5

# TODO: Remove in future
def list_subtract(list1, list2):
    """Subtract two lists and return the sorted result."""
    list1 = list1.copy()

    for x in list2:
        list1.remove(x)

    return list(sorted(list1))

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
        return _("{emoji} Red").format(emoji='❤️')
    if color == "b":
        return _("{emoji} Blue").format(emoji='💙')
    if color == "g":
        return _("{emoji} Green").format(emoji='💚')
    if color == "y":
        return _("{emoji} Yellow").format(emoji='💛')

# TODO: Move to card classs
def display_color_group(color, game):
    """Convert a color code to actual color name."""
    if color == "r":
        return __("{emoji} Red", game.translate).format(
            emoji='❤️')
    if color == "b":
        return __("{emoji} Blue", game.translate).format(
            emoji='💙')
    if color == "g":
        return __("{emoji} Green", game.translate).format(
            emoji='💚')
    if color == "y":
        return __("{emoji} Yellow", game.translate).format(
            emoji='💛')

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
