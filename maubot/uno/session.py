"""Хранилище игровых сессий."""

from aiogram import Bot
from loguru import logger

from maubot.uno.exceptions import (
    LobbyClosedError,
    NoGameInChatError,
)
from maubot.uno.game import UnoGame
from maubot.uno.player import Player


class SessionManager:
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    def __init__(self):
        self.bot: Bot = None
        self.games: dict[str, UnoGame] = {}
        self.user_to_chat: dict[int, int] = {}


    # Управление игроками в сессии
    # ============================

    def join(self, chat_id: int, user) -> None:
        """Добавляет нового игрока в игру.

        Более высокоуровневая функция, совершает больше проверок.
        """
        game = self.games.get(chat_id)
        if game is None:
            raise NoGameInChatError()
        if not game.open:
            raise  LobbyClosedError()

        game.add_player(user)
        self.user_to_chat[user.id] = chat_id
        logger.debug(self.user_to_chat)

    def leave(self, player: Player) -> None:
        """Убирает игрока из игры."""
        chat_id = self.user_to_chat.get(player.user.id)
        if chat_id is None:
            raise NoGameInChatError()

        game = self.games[chat_id]

        if player is game.player:
            game.next_turn()

        player.on_leave()
        game.players.remove(player)
        self.user_to_chat.pop(player.user.id)

        if len(game.players) <= 1:
            game.end()

    def get_player(self, user_id: int) -> Player | None:
        """Получает игрока по его id."""
        chat_id = self.user_to_chat.get(user_id)
        if chat_id is None:
            return None
        return self.games[chat_id].get_player(user_id)


    # Управление сессиями
    # ===================

    def create(self, chat_id: int) -> UnoGame:
        """Создает новую игру в чате."""
        logger.info("Create new session in chat {}", chat_id)
        game = UnoGame(self.bot, chat_id)
        self.games[chat_id] = game
        return game

    def remove(self, chat_id: int):
        """Полностью завершает игру в конкретном чате.

        Если вы хотите завершить текущий кон - воспользуйтесь методов
        `UnoGame.end()`.
        """
        try:
            game = self.games.pop(chat_id)
            for player in game.players:
                self.user_to_chat.pop(player.user.id)
        except KeyError as e:
            logger.warning(e)
            raise NoGameInChatError()
