"""Маршрутизация событий от движка."""

from loguru import logger

from mau.enums import GameEvents, GameState
from mau.events import Event
from maubot import markups, messages
from maubot.config import sm, stickers
from maubot.events.journal import EventRouter, MessageChannel
from maubot.messages import plural_form

er = EventRouter()


@er.event(GameEvents.SESSION_START)
async def start_session(event: Event, chan: MessageChannel) -> None:
    """Отправляет лобби, когда начинается новая игра в чате."""
    lobby_message = (
        f"{messages.game_status(event.game)}\n\n"
        f"🔥 {event.player.name}, Начинает новую игру!"
    )
    await chan.send_lobby(
        message=lobby_message,
        reply_markup=markups.lobby_markup(event.game),
    )


@er.event(GameEvents.SESSION_END)
async def end_session(event: Event, chan: MessageChannel) -> None:
    """Очищает устаревший канал сообщений."""
    sm._event_handler.remove_channel(event.game.room_id)


# Обработка событий игры
# ======================


@er.event(GameEvents.GAME_START)
async def start_game(event: Event, chan: MessageChannel) -> None:
    """Оповещает о начале новой игры."""
    await chan.send_lobby(
        message=messages.game_status(event.game),
        reply_markup=None,
    )
    await chan.clear()
    chan.set_markup(markups.turn_markup(event.game))
    await chan.send_card(stickers.normal[event.game.deck.top.to_str()])
    chan.add("🌳 Да начнётся <b>Новая игра!</b>!")
    chan.add(f"✨ Игру начинает {event.game.player.mention}.")
    chan.add(
        f"{messages.game_rules_list(event.game)}"
        "/close если не хотите чтобы вашей игре помешали.\n"
    )
    await chan.send()


@er.event(GameEvents.GAME_END)
async def end_game(event: Event, chan: MessageChannel) -> None:
    """Завершает игру в чате."""
    chan.add(messages.end_game_players(event.game.pm))
    chan.set_markup(markups.NEW_GAME_MARKUP)
    await chan.send()
    sm.remove(event.game.room_id)


@er.event(GameEvents.GAME_JOIN)
async def join_player(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if not event.game.started:
        lobby_message = (
            f"{messages.game_status(event.game)}\n\n"
            f"👋 {event.player.mention} зашёл в комнату!"
        )
        await chan.send_lobby(
            message=lobby_message,
            reply_markup=markups.lobby_markup(event.game),
        )
        return

    chan.add(f"🍰 Добро пожаловать в игру, {event.player.mention}!")
    await chan.send()


@er.event(GameEvents.GAME_LEAVE)
async def leave_player(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь вышел из игры."""
    if chan.lobby_message is not None and not event.game.started:
        lobby_message = (
            f"{messages.game_status(event.game)}\n\n"
            f"👋 {event.player.mention} покидает комнату!"
        )
        await chan.send_lobby(
            message=lobby_message,
            reply_markup=markups.lobby_markup(event.game),
        )
        return

    if event.data == "win":
        chan.add("👑 закончил(а)!\n")
    else:
        chan.add(f"👋 {event.player.mention} покидает нас.")

    # Это может бывать выход из игры до её начала
    if not event.game.started:
        chan.set_markup(None)


@er.event(GameEvents.GAME_SELECT_COLOR)
async def select_card_color(event: Event, chan: MessageChannel) -> None:
    """Какой новый цвет был выбран для карты."""
    chan.add(f"🎨 Я выбираю {event.data}!")


@er.event(GameEvents.GAME_SELECT_PLAYER)
async def twist_hand(event: Event, chan: MessageChannel) -> None:
    """Сообщает об обмене картами между пользователями."""
    other_player = event.game.pm.get_or_none(event.data)
    if other_player is None:
        chan.add("🍺 Куда подевался второй игрок?")
        return

    # Событие происходит после выполнения действия, потому так считаем карты
    chan.add(
        f"🤝 {event.player.name} ({len(other_player.hand)} 🃏) "
        f"и {other_player.mention} ({len(event.player.hand)} 🃏) "
        "обменялись картами.\n"
    )


@er.event(GameEvents.GAME_TURN)
async def next_turn(event: Event, chan: MessageChannel) -> None:
    """Начала следующего хода."""
    await chan.clear()
    chan.set_markup(markups.turn_markup(event.game))
    cards = len(event.game.player.hand)
    chan.add(
        f"\n🍰 <b>ход</b>: {event.game.player.mention} "
        f"(🃏 {cards} {plural_form(cards, ('карту', 'карты', 'карт'))})"
    )
    await chan.send()


@er.event(GameEvents.GAME_ROTATE)
async def rotate_cards(event: Event, chan: MessageChannel) -> None:
    """Все игрока обменялись картами, возвращает сколько карт у игроков."""
    chan.add("🌀 Обмениваемся <b>картами</b>!")
    chan.add(messages.players_list(event.game.pm, event.game.reverse, False))


@er.event(GameEvents.GAME_STATE)
async def update_game_state(event: Event, chan: MessageChannel) -> None:
    """При изменении игрового состояния."""
    state = GameState(int(event.data))
    if state == GameState.SHOTGUN:
        current = (
            event.game.shotgun.cur
            if event.game.rules.single_shotgun.status
            else event.player.shotgun.cur
        )
        chan.add(
            "💼 <b>У нас для Вас деловое предложение</b>!\n\n"
            f"Вы можете <b>взять {event.game.take_counter} карт</b> "
            "или попробовать <b>выстрелить из револьвера</b>.\n"
            "Если вам повезёт, то карты будет брать следующий игрок.\n"
            f"🔫 Из револьвера стреляли {current} / 8 раз\n."
        )
        chan.set_markup(markups.SHOTGUN_MARKUP)

    elif state == GameState.TWIST_HAND:
        chan.add("✨ С кем бы обменяться картами ..")
        chan.set_markup(
            markups.select_player(
                event.game.pm, event.game.rules.twist_hand_pass.status
            )
        )

    elif state == GameState.CHOOSE_COLOR:
        chan.add("✨ Какой бы выбрать цвет ...")
        chan.set_markup(markups.SELECT_COLOR)

    elif state == GameState.TAKE:
        chan.set_markup(markups.turn_markup(event.game))

    else:
        logger.warning("Unprocessed state {}", state)
        return

    await chan.send()


# Обработка действий игрока
# =========================


@er.event(GameEvents.PLAYER_UNO)
async def say_uno(event: Event, chan: MessageChannel) -> None:
    """Оповещает что у игрока осталась одна карта в руке."""
    chan.add("\n🌟 <b>UNO!</b>")


@er.event(GameEvents.PLAYER_TAKE)
async def player_take_cards(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь взял карты."""
    if chan.lobby_message is not None:
        return

    if event.player == event.game.player:
        chan.add(
            f"🃏 Беру {event.data} "
            f"{plural_form(int(event.data), ('карту', 'карты', 'карт'))}"
        )
    else:
        chan.add(
            f"🃏 {event.player.mention} Берёт {event.data} "
            f"{plural_form(int(event.data), ('карту', 'карты', 'карт'))}"
        )

    await chan.send()


@er.event(GameEvents.PLAYER_BLUFF)
async def player_bluffing(event: Event, chan: MessageChannel) -> None:
    """Проверка игрока на блеф."""
    if event.game.bluff_player is None:
        chan.add("🎩 <b>Никто не блефовал</b>!")
        return

    player, bluff_flag = event.game.bluff_player
    if player is not None and bluff_flag:
        chan.add("🔎 <b>Замечен блеф</b>!")
    else:
        chan.add(f"🎩 {player.mention} <b>Честный игрок</b>!")


@er.event(GameEvents.PLAYER_INTERVENED)
async def on_intervention(event: Event, chan: MessageChannel) -> None:
    """Когда игрок вмешивается в игру и перехватывает ход."""
    chan.add(f"⚡ {event.player.mention} <b>навёл суеты!</b>")
    await chan.send()
