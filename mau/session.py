"""Хранилище игровых сессий.

Занимается общей обработкой всех существующих сессий.
Отвечает за создание новых игр и привязыванию их к чату.
"""

from aiogram import Bot
from loguru import logger

from mau.exceptions import (
    LobbyClosedError,
    NoGameInChatError,
)
from mau.game import UnoGame
from mau.journal import TelegramJournal
from mau.player import BaseUser, Player


class SessionManager:
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    def __init__(self) -> None:
        # FIXME: Отвязать от бота
        self.bot: Bot | None = None
        self.games: dict[str, UnoGame] = {}
        self.user_to_chat: dict[str, str] = {}

    # Управление игроками в сессии
    # ================W============

    def join(self, room_id: str, user: BaseUser) -> None:
        """Добавляет нового игрока в игру.

        Более высокоуровневая функция, совершает больше проверок.
        """
        game = self.games.get(room_id)
        if game is None:
            raise NoGameInChatError()
        if not game.open:
            raise LobbyClosedError()

        game.add_player(user)
        self.user_to_chat[user.id] = room_id
        logger.debug(self.user_to_chat)

    def leave(self, player: Player) -> None:
        """Убирает игрока из игры."""
        room_id = self.user_to_chat.get(player.user_id)
        if room_id is None:
            raise NoGameInChatError()

        game = self.games[room_id]

        if player is game.player:
            game.next_turn()

        player.on_leave()
        game.players.remove(player)
        self.user_to_chat.pop(player.user_id)

        if len(game.players) <= 1:
            game.end()

    def get_player(self, user_id: str) -> Player | None:
        """Получает игрока по его id."""
        room_id = self.user_to_chat.get(user_id)
        if room_id is None:
            return None
        return self.games[room_id].get_player(user_id)

    # Управление сессиями
    # ===================

    def create(self, room_id: str) -> UnoGame:
        """Создает новую игру в чате."""
        if self.bot is None:
            raise ValueError("Ypu must set bot instance to create games")

        logger.info("Create new session in chat {}", room_id)
        game = UnoGame(TelegramJournal(room_id, self.bot), room_id)
        self.games[room_id] = game
        return game

    def remove(self, room_id: str) -> None:
        """Полностью завершает игру в конкретном чате.

        Если вы хотите завершить текущий кон - воспользуйтесь методов
        `UnoGame.end()`.
        """
        try:
            game: UnoGame = self.games.pop(room_id)
            for player in game.players:
                self.user_to_chat.pop(player.user_id)
        except KeyError as e:
            logger.warning(e)
            raise NoGameInChatError() from e


# Привязанный к платформе менеджер сессий
# =======================================
