from loguru import logger

from maubot.uno.game import UnoGame, GameRules
from maubot.uno.exceptions import NoGameInChatError, LobbyClosedError, AlreadyJoinedError


class SessionManager:

    def __init__(self):
        self.games: dict[str, ] = {}

    def join(self, chat_id: int, user):
        game = self.games.get(chat_id)
        if game is None:
            raise NoGameInChatError()
        if not game.open:
            raise  LobbyClosedError()
        
        player = game.get_player(user.id)
        if player is not None:
            raise AlreadyJoinedError()


    def leave(self):
        pass


    def create(self, chat_id: int, rules: GameRules) -> UnoGame:
        logger.info("Create new session in chat {}". chat)
        game = UnoGame(chat_id, rules)
        self.games[chat_id] = game
        return game

    def end(self):
        pass
