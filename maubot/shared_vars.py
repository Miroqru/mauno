from telegram.ext import Updater

from maubot.config import TOKEN, WORKERS
from maubot.uno.game_manager import GameManager

# FIXME: Use Aiogram dispather
# TODO: Mode to con fig file
gm = GameManager()
updater = Updater(token=TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher
