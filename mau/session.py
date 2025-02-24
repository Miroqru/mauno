"""Хранилище игровых сессий.

Занимается общей обработкой всех существующих сессий.
Отвечает за создание новых игр и привязыванию их к чату.
"""

from loguru import logger

from mau.events import BaseEventHandler, Event, EventJournal, GameEvents
from mau.exceptions import (
    LobbyClosedError,
    NoGameInChatError,
)
from mau.game import UnoGame
from mau.player import BaseUser, Player


class SessionManager:
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    def __init__(self) -> None:
        self.games: dict[str, UnoGame] = {}
        self.user_to_chat: dict[str, str] = {}
        self.chat_journal: dict[str, BaseEventHandler] = {}

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
        self.chat_journal[room_id].push(
            Event(user.id, GameEvents.SESSION_JOIN, "", game)
        )

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
        self.chat_journal[room_id].push(
            Event(player.user_id, GameEvents.SESSION_LEAVE, "", game)
        )

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

    def create(
        self, room_id: str, user: BaseUser, event_handler: BaseEventHandler
    ) -> UnoGame:
        """Создает новую игру в чате."""
        logger.info("User {} Create new game session in {}", user, room_id)
        journal = EventJournal(room_id, event_handler)
        game = UnoGame(journal, room_id, user)
        self.games[room_id] = game
        self.user_to_chat[user.id] = room_id
        self.chat_journal[room_id] = event_handler
        self.chat_journal[room_id].push(
            Event(user.id, GameEvents.SESSION_START, "", game)
        )

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
            self.chat_journal[room_id].push(
                Event("mau", GameEvents.SESSION_START, "", game)
            )
        except KeyError as e:
            logger.warning(e)
            raise NoGameInChatError() from e
