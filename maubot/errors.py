class NoGameInChatError(Exception):
    """If there is no active game created in the chat.

    For example, when a user tries to join a game that does not exist.
    """

    pass

class AlreadyJoinedError(Exception):
    """When the user tries to reconnect to the game."""

    pass

class LobbyClosedError(Exception):
    """When a user tries to join a closed lobby."""

    pass

class NotEnoughPlayersError(Exception):
    """When there are not enough players to start the game."""

    pass

class DeckEmptyError(Exception):
    """When the deck runs out of cards."""

    pass
