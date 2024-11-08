from telegram.ext import Updater

from config import TOKEN, WORKERS
from database import db
from game_manager import GameManager

gm = GameManager()
updater = Updater(token=TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher
