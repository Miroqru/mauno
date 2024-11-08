from telegram.ext import Updater

from maubot.config import TOKEN, WORKERS
from maubot.game_manager import GameManager

gm = GameManager()
updater = Updater(token=TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher
