from apscheduler.jobstores.base import JobLookupError
from loguru import logger
from telegram.ext import CallbackContext

import maubot.uno.card as c
from maubot.config import MIN_FAST_TURN_TIME, TIME_REMOVAL_AFTER_SKIP
from maubot.database import UserSetting
from maubot.shared_vars import gm
from maubot.uno.errors import DeckEmptyError, NotEnoughPlayersError
from maubot.utils import display_name, game_is_running, send_async

# TODO: Перенести функции в соответствующие классы

# TODO: do_skip() could get executed in another thread (it can be a job),
# so it looks like it can't use game.translate?
def do_skip(bot, player, job_queue=None):
    logger.info("Skip action: {} q={}", player, job_queue)

    game = player.game
    chat = game.chat
    skipped_player = game.current_player
    next_player = game.current_player.next

    if skipped_player.waiting_time > 0:
        skipped_player.anti_cheat += 1
        skipped_player.waiting_time -= TIME_REMOVAL_AFTER_SKIP
        skipped_player.waiting_time = max(skipped_player.waiting_time, 0)

        try:
            skipped_player.draw()
        except DeckEmptyError as e:
            logger.error(e)

        n = skipped_player.waiting_time
        send_async(bot, chat.id, text=(
            "Waiting time to skip this player has "
            f"been reduced to {n} seconds.\n"
            f"Next player: {display_name(next_player.user)}"
        ))
        logger.info("{} was skipped! ", display_name(player.user))
        game.turn()
        if job_queue:
            start_player_countdown(bot, game, job_queue)

    else:
        try:
            gm.leave_game(skipped_player.user, chat)
            send_async(bot, chat.id, text=(
                f"{display_name(skipped_player.user)} ran out of time "
                "and has been removed from the game!\n"
                f"Next player: {display_name(next_player.user)}"
            ))
            logger.info("{} was skipped!", display_name(next_player.user))
            if job_queue:
                start_player_countdown(bot, game, job_queue)

        except NotEnoughPlayersError as e:
            logger.warning(e)
            send_async(bot, chat.id, text=(
                f"{display_name(skipped_player.user)} ran out of time "
                "and has been removed from the game!\n"
                "Game ended!"
            ))
            gm.end_game(chat, skipped_player.user)

def do_play_card(bot, player, result_id):
    """Plays the selected card and sends an update to the group if needed."""
    logger.info("Push card from {} with {}", player, result_id)

    card = c.from_str(result_id)
    player.play(card)
    game = player.game
    chat = game.chat
    user = player.user

    # update user stats
    us = UserSetting.get(id=user.id)
    if us is None:
        us = UserSetting(id=user.id)

    if us.stats:
        us.cards_played += 1

    # generate send message
    result_text = ""

    if len(player.cards) == 1:
        result_text += "UNO!\n"

    if game.choosing_color:
        result_text += "I choose the color...\n"

    if len(player.cards) == 0:
        result_text += f"{user.first_name} won!\n"

        if us.stats:
            us.games_played += 1
            if game.players_won == 0:
                us.first_places += 1

        game.players_won += 1

        try:
            gm.leave_game(user, chat)
        except NotEnoughPlayersError:
            result_text += "\nGame ended!"

            # update other user info
            other_user = UserSetting.get(id=game.current_player.user.id)
            if other_user is not None and other_user.stats:
                other_user.games_played += 1

            gm.end_game(chat, user)

    send_async(bot, chat.id, text=result_text)

def do_draw(bot, player):
    logger.info("{} draw cards", player)
    game = player.game
    draw_counter_before = game.draw_counter

    try:
        player.draw()
    except DeckEmptyError:
        send_async(bot, player.game.chat.id,
            text="There are no more cards in the deck."
        )

    if ((game.last_card.value == c.DRAW_TWO or
        game.last_card.special == c.DRAW_FOUR)
        and draw_counter_before > 0
    ):
        game.turn()

def do_call_bluff(bot, player):
    logger.info("{} call bluff", player)
    game = player.game
    chat = game.chat

    if player.prev.bluffing:
        send_async(bot, chat.id, text=(
            f"Bluff called! Giving 4 cards to {player.prev.user.first_name}",
        ))

        try:
            player.prev.draw()
        except DeckEmptyError as e:
            logger.warning(e)
            send_async(bot, player.game.chat.id,
                text="There are no more cards in the deck.",
            )

    else:
        game.draw_counter += 2
        send_async(bot, chat.id, text=(
            f"{player.prev.user.first_name} didn't bluff!\n"
            "Giving 6 cards to {player.user.first_name}",
        ))
        try:
            player.draw()
        except DeckEmptyError as e:
            logger.warning(e)
            send_async(bot, player.game.chat.id,
                text="There are no more cards in the deck."
            )

    game.turn()


class Countdown:
    def __init__(self, player, job_queue):
        self.player = player or None
        self.job_queue = job_queue or None

def start_player_countdown(bot, game, job_queue):
    player = game.current_player
    time = max(player.waiting_time, MIN_FAST_TURN_TIME)

    if game.mode != 'fast':
        return

    if game.job:
        try:
            game.job.schedule_removal()
        except JobLookupError as e:
            logger.error(e)

    job = job_queue.run_once(
        skip_job, time,
        context=Countdown(player, job_queue)
    )

    logger.info("Started countdown for player: {}. {} seconds.",
        display_name(player.user), time
    )
    player.game.job = job

def skip_job(context: CallbackContext):
    player = context.job.context.player
    game = player.game
    if game_is_running(game):
        job_queue = context.job.context.job_queue
        do_skip(context.bot, player, job_queue)
