import logging
from datetime import datetime

from loguru import logger
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
)

import maubot.uno.card as c
from maubot import settings, simple_commands
from maubot.config import MIN_PLAYERS, WAITING_TIME
from maubot.results import (
    add_call_bluff,
    add_card,
    add_choose_color,
    add_draw,
    add_gameinfo,
    add_mode_classic,
    add_mode_fast,
    add_mode_text,
    add_mode_wild,
    add_no_game,
    add_not_started,
    add_other_cards,
    add_pass,
)
from maubot.shared_vars import dispatcher, gm, updater
from maubot.simple_commands import help_handler
from maubot.uno.actions import (
    do_call_bluff,
    do_draw,
    do_play_card,
    do_skip,
    start_player_countdown,
)
from maubot.uno.errors import (
    NoGameInChatError,
    NotEnoughPlayersError,
)
from maubot.utils import (
    TIMEOUT,
    answer_async,
    display_name,
    error,
    game_is_running,
    send_async,
    user_is_creator,
    user_is_creator_or_admin,
)

logging.basicConfig(
    format='%(asctime)s: %(name)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
logging.getLogger('apscheduler').setLevel(logging.WARNING)


# Handlers
# ========

def notify_me(update: Update, context: CallbackContext):
    """Handle for /notify_me command, pm people for next game."""
    chat_id = update.message.chat_id
    if update.message.chat.type == 'private':
        send_async(bot, chat_id, text=(
            "Send this command in a group to be notified "
            "when a new game is started there."
        ))
    else:
        try:
            gm.remind_dict[chat_id].add(update.message.from_user.id)
        except KeyError as e:
            logger.warning(e)
            gm.remind_dict[chat_id] = {update.message.from_user.id}

def kill_game(update: Update, context: CallbackContext):
    """Handle for the /kill command."""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if update.message.chat.type == 'private':
        help_handler(update, context)
        return

    if not games:
        send_async(context.bot, chat.id,
            text="There is no running game in this chat.")
        return

    game = games[-1]
    if user_is_creator_or_admin(user, game, context.bot, chat):
        try:
            gm.end_game(chat, user)
            send_async(context.bot, chat.id, text="Game ended!")
        except NoGameInChatError:
            send_async(context.bot, chat.id, text=(
                    "The game is not started yet. "
                    "Join the game with /join and start the game with /start"
                ),
                reply_to_message_id=update.message.message_id
            )
    else:
        send_async(context.bot, chat.id, text=(
                f"Only the game creator ({game.starter.first_name})"
                " and admin can do that."
            ),
            reply_to_message_id=update.message.message_id
        )

def leave_game(update: Update, context: CallbackContext):
    """Handle for the /leave command."""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)
    if player is None:
        return send_async(context.bot, chat.id,
            text="You are not playing in a game in this chat.",
            reply_to_message_id=update.message.message_id
        )

    try:
        gm.leave_game(user, chat)
    except NoGameInChatError:
        send_async(context.bot, chat.id,
            text="You are not playing in a game in this group.",
            reply_to_message_id=update.message.message_id
        )
    except NotEnoughPlayersError:
        gm.end_game(chat, user)
        send_async(context.bot, chat.id, text="Game ended!")
    else:
        game = player.game
        if game.started:
            send_async(context.bot, chat.id,
                text=f"Okay. Next Player: {display_name(game.current_player.user)}",
                reply_to_message_id=update.message.message_id
            )
        else:
            send_async(context.bot, chat.id,
                text=f"{display_name(user)} left the game before it started.",
                reply_to_message_id=update.message.message_id
            )

def kick_player(update: Update, context: CallbackContext):
    """Handle for the /kick command."""
    if update.message.chat.type == 'private':
        help_handler(update, context)
        return

    chat = update.message.chat
    user = update.message.from_user

    try:
        game = gm.chatid_games[chat.id][-1]
    except (KeyError, IndexError) as e:
        logger.warning(e)
        return send_async(context.bot, chat.id, text=(
                "No game is running at the moment. Create a new game with /new"
            ),
            reply_to_message_id=update.message.message_id
        )

    if not game.started:
        return send_async(context.bot, chat.id, text=(
                "The game is not started yet. "
                "Join the game with /join and start the game with /start"
            ),
            reply_to_message_id=update.message.message_id
        )

    if not user_is_creator_or_admin(user, game, context.bot, chat):
        return send_async(context.bot, chat.id, text=(
                f"Only the game creator ({game.starter.first_name}) and admin can do that."
            ),
            reply_to_message_id=update.message.message_id
        )

    if update.message.reply_to_message:
        kicked = update.message.reply_to_message.from_user
        try:
            gm.leave_game(kicked, chat)
        except NoGameInChatError:
            return send_async(context.bot, chat.id, text=(
                    f"Player {display_name(kicked)} is not found in the current game."
                ),
                reply_to_message_id=update.message.message_id
            )
        except NotEnoughPlayersError:
            gm.end_game(chat, user)
            return send_async(context.bot, chat.id, text=(
                f"{display_name(kicked)} was kicked by {display_name(user)}\n"
                "Game ended!"
            ))

        send_async(context.bot, chat.id,
            text=(f"{display_name(kicked)} was kicked by {display_name(user)}")
        )

    else:
        return send_async(context.bot, chat.id,
            text="Please reply to the person you want to kick and type /kick again.",
            reply_to_message_id=update.message.message_id
        )

    send_async(context.bot, chat.id,
        text=f"Okay. Next Player: {display_name(game.current_player.user)}",
        reply_to_message_id=update.message.message_id
    )

def skip_player(update: Update, context: CallbackContext):
    """Handle for the /skip command."""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)
    if not player:
        return send_async(context.bot, chat.id,
            text="You are not playing in a game in this chat."
        )

    game = player.game
    skipped_player = game.current_player

    started = skipped_player.turn_started
    now = datetime.now()
    delta = (now - started).seconds

    # You can't skip if the current player still has time left
    # You can skip yourself even if you have time left (you'll still draw)
    if delta < skipped_player.waiting_time and player != skipped_player:
        send_async(context.bot, chat.id,
            text=f"Please wait {skipped_player.waiting_time - delta} seconds",
            reply_to_message_id=update.message.message_id
        )
    else:
        do_skip(context.bot, player)


# Manage lobby command
# ====================

def start_game(update: Update, context: CallbackContext):
    """Handle for the /start command."""
    if update.message.chat.type != 'private':
        chat = update.message.chat

        else:
            game.start()
            choice = [[
                InlineKeyboardButton(
                    text="Make your choice!",
                    switch_inline_query_current_chat=''
            )]]
            first_message = (
                f"First player: {display_name(game.current_player.user)}\n"
                "Use /close to stop people from joining the game.\n"
            )

            def send_first():
                """Send the first card and player."""
                context.bot.sendSticker(chat.id,
                    sticker=c.STICKERS[str(game.last_card)], timeout=TIMEOUT
                )

                context.bot.sendMessage(chat.id,
                    text=first_message,
                    reply_markup=InlineKeyboardMarkup(choice), timeout=TIMEOUT
                )

            dispatcher.run_async(send_first)
            start_player_countdown(context.bot, game, context.job_queue)

def close_game(update: Update, context: CallbackContext):
    """Handle for the /close command."""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        return send_async(context.bot, chat.id,
            text="There is no running game in this chat."
        )

    game = games[-1]
    if user.id in game.owner:
        game.open = False
        return send_async(context.bot, chat.id, text=(
            "Closed the lobby. No more players can join this game."
        ))
    else:
        return send_async(context.bot, chat.id,
            text=f"Only the game creator ({game.starter.first_name}) and admin can do that.",
            reply_to_message_id=update.message.message_id
        )

def open_game(update: Update, context: CallbackContext):
    """Handle for the /open command."""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        return send_async(context.bot, chat.id,
            text="There is no running game in this chat."
        )

    game = games[-1]
    if user.id in game.owner:
        game.open = True
        return send_async(context.bot, chat.id,
            text="Opened the lobby. New players may /join the game."
        )
    else:
        return send_async(context.bot, chat.id,
            text=f"Only the game creator ({game.starter.first_name}) and admin can do that.",
            reply_to_message_id=update.message.message_id
        )


# Events
# ======

def status_update(update: Update, context: CallbackContext):
    """Remove player from game if user leaves the group."""
    chat = update.message.chat
    if not update.message.left_chat_member:
        return

    user = update.message.left_chat_member
    try:
        gm.leave_game(user, chat)
    except NoGameInChatError as e:
        logger.error(e)
    except NotEnoughPlayersError:
        gm.end_game(chat, user)
        send_async(context.bot, chat.id, text="Game ended!")
    else:
        send_async(context.bot, chat.id,
            text=f"Removing {display_name(user)} from the game"
        )


# Callback queries
# ================

def reset_waiting_time(bot, player):
    """Reset waiting time for a player and sends a notice to the group."""
    chat = player.game.chat

    if player.waiting_time < WAITING_TIME:
        player.waiting_time = WAITING_TIME
        send_async(bot, chat.id, text=(
            f"Waiting time for {display_name(player.user)} has been reset to {WAITING_TIME} seconds"
        ))

def select_game(update: Update, context: CallbackContext):
    """Handle for callback queries to select the current game."""
    chat_id = int(update.callback_query.data)
    user_id = update.callback_query.from_user.id
    players = gm.userid_players[user_id]
    for player in players:
        if player.game.chat.id == chat_id:
            gm.userid_current[user_id] = player
            break
    else:
        return send_async(context.bot, update.callback_query.message.chat_id,
            text="Game not found."
        )

    def selected():
        back = [[InlineKeyboardButton(
            text="Back to last group", switch_inline_query=''
        )]]
        context.bot.answerCallbackQuery(update.callback_query.id,
            text="Please switch to the group you selected!",
            show_alert=False,
            timeout=TIMEOUT
        )
        context.bot.editMessageText(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=(
                f"Selected group: {gm.userid_current[user_id].game.chat.title}\n"
                "<b>Make sure that you switch to the correct group!</b>"
            ),
            reply_markup=InlineKeyboardMarkup(back),
            parse_mode=ParseMode.HTML,
            timeout=TIMEOUT
        )

    dispatcher.run_async(selected)

def reply_to_query(update: Update, context: CallbackContext):
    """Handle for inline queries.

    Builds the result list for inline queries and answers to the client.
    """
    results = []
    switch = None

    try:
        user = update.inline_query.from_user
        user_id = user.id
        players = gm.userid_players[user_id]
        player = gm.userid_current[user_id]
        game = player.game
    except KeyError as e:
        logger.warning(e)
        add_no_game(results)
    else:
        # The game has not started.
        # The creator may change the game mode, other users just get a
        # "game has not started" message.
        if not game.started:
            if user_is_creator(user, game):
                add_mode_classic(results)
                add_mode_fast(results)
                add_mode_wild(results)
                add_mode_text(results)
            else:
                add_not_started(results)

        elif user_id == game.current_player.user.id:
            if game.choosing_color:
                add_choose_color(results, game)
                add_other_cards(player, results, game)
            else:
                if not player.drew:
                    add_draw(player, results)
                else:
                    add_pass(results, game)

                if game.last_card.special == c.DRAW_FOUR and game.draw_counter:
                    add_call_bluff(results, game)

                playable = player.playable_cards()
                added_ids = list()  # Duplicates are not allowed
                for card in sorted(player.cards):
                    add_card(game, card, results,
                        can_play=(
                            card in playable and str(card) not in added_ids
                        )
                    )
                    added_ids.append(str(card))
                add_gameinfo(game, results)

        elif user_id != game.current_player.user.id or not game.started:
            for card in sorted(player.cards):
                add_card(game, card, results, can_play=False)

        else:
            add_gameinfo(game, results)

        for result in results:
            result.id += ':%d' % player.anti_cheat

        if players and game and len(players) > 1:
            switch = f'Current game: {game.chat.title}'

    answer_async(context.bot, update.inline_query.id, results, cache_time=0,
        switch_pm_text=switch, switch_pm_parameter='select'
    )

def process_result(update: Update, context: CallbackContext):
    """Handle for chosen inline results.

    Checks the players actions and acts accordingly.
    """
    try:
        user = update.chosen_inline_result.from_user
        player = gm.userid_current[user.id]
        game = player.game
        result_id = update.chosen_inline_result.result_id
        chat = game.chat
    except (KeyError, AttributeError) as e:
        logger.error(e)
        return

    logger.warning("Selected result: {}", result_id)
    result_id, anti_cheat = result_id.split(':')
    last_anti_cheat = player.anti_cheat
    player.anti_cheat += 1

    # Handle result
    if result_id in ('hand', 'gameinfo', 'nogame') or len(result_id) == 36:
        return

    elif result_id.startswith('mode_'):
        # First 5 characters are 'mode_', the rest is the game mode.
        mode = result_id[5:]
        game.set_mode(mode)
        logger.info("Gamemode changed to {}", mode)
        return send_async(context.bot, chat.id,
            text=f"Gamemode changed to {mode}"
        )

    elif int(anti_cheat) != last_anti_cheat:
        return send_async(context.bot, chat.id,
            text=f"Cheat attempt by {display_name(player.user)}",
        )

    elif result_id == 'call_bluff':
        reset_waiting_time(context.bot, player)
        do_call_bluff(context.bot, player)

    elif result_id == 'draw':
        reset_waiting_time(context.bot, player)
        do_draw(context.bot, player)

    elif result_id == 'pass':
        game.turn()

    elif result_id in c.COLORS:
        game.choose_color(result_id)

    else:
        reset_waiting_time(context.bot, player)
        do_play_card(context.bot, player, result_id)

    # passing the move to the next player
    if game_is_running(game):
        send_async(context.bot, chat.id,
            text=f"Next player: {display_name(game.current_player.user)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="Make your choice!",
                    switch_inline_query_current_chat=''
                )
            ]])
        )
        start_player_countdown(context.bot, game, context.job_queue)


# Main function
# =============

def start_bot():
    """Prepare and launch bot."""
    # Add all handlers to the dispatcher and run the bot
    dispatcher.add_handler(InlineQueryHandler(reply_to_query))
    dispatcher.add_handler(ChosenInlineResultHandler(
        process_result, pass_job_queue=True
    ))
    dispatcher.add_handler(CallbackQueryHandler(select_game))
    dispatcher.add_handler(CommandHandler(
        'start', start_game, pass_args=True, pass_job_queue=True
    ))
    dispatcher.add_handler(CommandHandler('kill', kill_game))
    dispatcher.add_handler(CommandHandler('leave', leave_game))
    dispatcher.add_handler(CommandHandler('kick', kick_player))
    dispatcher.add_handler(CommandHandler('open', open_game))
    dispatcher.add_handler(CommandHandler('close', close_game))
    dispatcher.add_handler(CommandHandler('skip', skip_player))
    dispatcher.add_handler(CommandHandler('notify_me', notify_me))
    dispatcher.add_handler(MessageHandler(Filters.status_update, status_update))
    dispatcher.add_error_handler(error)
