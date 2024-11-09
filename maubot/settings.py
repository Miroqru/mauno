from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
)

from maubot.database import UserSetting
from maubot.shared_vars import dispatcher
from maubot.utils import send_async

# TODO: Использовать aiogram router


# FIXME: Использовать aiogram обработчик
def show_settings(update: Update, context: CallbackContext):
    chat = update.message.chat
    if update.message.chat.type != "private":
        send_async(context.bot, chat.id,
            text="Please edit your settings in a private chat with " "the bot."
        )
        return

    us = UserSetting.get(id=update.message.from_user.id)
    if us is None:
        us = UserSetting(id=update.message.from_user.id)

    if not us.stats:
        stats = "📊 Enable statistics"
    else:
        stats = "❌ Delete all statistics"

    kb = [[stats]]
    send_async(
        context.bot, chat.id, text="🔧 Settings",
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True),
    )

# FIXME: Использовать aiogram обработчик
def kb_select(update: Update, context: CallbackContext):
    chat = update.message.chat
    user = update.message.from_user
    option = context.match[1]

    if option == "📊":
        us = UserSetting.get(id=user.id)
        us.stats = True
        send_async(context.bot, chat.id, text="Enabled statistics!")

    elif option == "❌":
        us = UserSetting.get(id=user.id)
        us.stats = False
        us.first_places = 0
        us.games_played = 0
        us.cards_played = 0
        send_async(context.bot, chat.id,
            text="Deleted and disabled statistics!"
        )

# FIXME: Использовать aiogram router
def register():
    dispatcher.add_handler(CommandHandler("settings", show_settings))
    dispatcher.add_handler(
        MessageHandler(Filters.regex("^([" + "📊" + "❌" + "]) .+$"), kb_select)
    )