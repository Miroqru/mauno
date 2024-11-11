from loguru import logger

from maubot.promotions import send_promotion_async
from maubot.uno.errors import (
    AlreadyJoinedError,
    LobbyClosedError,
    NoGameInChatError,
    NotEnoughPlayersError,
)
from maubot.uno.game import Game
from maubot.uno.player import Player

MIN_GAME_PLAYERS = 3

class GameManager(object):
    """Manages all running games by using a confusing amount of dicts."""

    def __init__(self):
        self.chatid_games = {}
        self.userid_players = {}
        self.userid_current = {}
        self.remind_dict = {}


    def join_game(self, user, chat):
        """Create a player from the Telegram user and add it to the game."""
        logger.info("Joining {} game with id {}", user, chat.id)


        if not game.open:
            raise LobbyClosedError()

        if user.id not in self.userid_players:
            self.userid_players[user.id] = list()

        players = self.userid_players[user.id]

        # Don not re-add a player and remove the player from previous games in
        # this chat, if he is in one of them
        for player in players:
            if player in game.players:
                raise AlreadyJoinedError()

        try:
            self.leave_game(user, chat)
        except NoGameInChatError:
            pass
        except NotEnoughPlayersError:
            self.end_game(chat, user)

            if user.id not in self.userid_players:
                self.userid_players[user.id] = list()

            players = self.userid_players[user.id]

        player = Player(game, user)
        if game.started:
            player.draw_first_hand()

        players.append(player)
        self.userid_current[user.id] = player

    def leave_game(self, user, chat):
        """Remove a player from its current game."""
        logger.info("Leaving {} game with id {}", user, chat.id)
        
        player = self.player_for_user_in_chat(user, chat)
        players = self.userid_players.get(user.id, [])

        if not player:
            games = self.chatid_games[chat.id]
            for g in games:
                for p in g.players:
                    if p.user.id == user.id:
                        if p == g.current_player:
                            g.turn()

                        p.leave()
                        return

            raise NoGameInChatError

        game = player.game

        if len(game.players) < MIN_GAME_PLAYERS:
            raise NotEnoughPlayersError()

        if player is game.current_player:
            game.turn()

        player.leave()
        players.remove(player)

        # If this is the selected game, switch to another
        if self.userid_current.get(user.id, None) is player:
            if players:
                self.userid_current[user.id] = players[0]
            else:
                del self.userid_current[user.id]
                del self.userid_players[user.id]

    def end_game(self, chat, user):
        """End a game."""
        logger.info("Game in chat {} ended", chat.id)
        send_promotion_async(chat, chance=0.15)

        # Find the correct game instance to end
        player = self.player_for_user_in_chat(user, chat)

        if not player:
            raise NoGameInChatError

        game = player.game

        # Clear game
        for game_player in game.players:
            user_players = self.userid_players.get(
                game_player.user.id, []
            )

            try:
                user_players.remove(game_player)
            except ValueError:
                pass

            if user_players:
                try:
                    self.userid_current[game_player.user.id] = user_players[0]
                except KeyError:
                    pass
            else:
                try:
                    self.userid_players.pop(game_player.user.id)
                except KeyError:
                    pass

                try:
                    self.userid_current.pop(game_player.user.id)
                except KeyError:
                    pass

        self.chatid_games[chat.id].remove(game)
        if not self.chatid_games[chat.id]:
            del self.chatid_games[chat.id]

    def player_for_user_in_chat(self, user, chat):
        players = self.userid_players.get(user.id, list())
        for player in players:
            if player.game.chat.id == chat.id:
                return player
        return None
