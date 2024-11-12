from loguru import logger

from maubot.uno.exceptions import (
    LobbyClosedError,
    NoGameInChatError,
)
from maubot.uno.game import GameRules, UnoGame


class SessionManager:
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    def __init__(self):
        self.games: dict[str, UnoGame] = {}


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


    # Управление сессиями
    # ===================

    def create(self, chat_id: int) -> UnoGame:
        """Создает новую игру в чате."""
        logger.info("Create new session in chat {}", chat_id)
        game = UnoGame(chat_id)
        self.games[chat_id] = game
        return game

    def remove(self, chat_id: int):
        """Полностью завершает игру в конкретном чате.

        Если вы хотите завершить текущий кон - воспользуйтесь методов
        `UnoGame.end()`.
        """
        try:
            self.games.pop(chat_id)
        except KeyError as e:
            logger.warning(e)
            raise NoGameInChatError()
