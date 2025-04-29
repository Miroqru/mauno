"""Маршрутизация событий от движка."""

from loguru import logger

from mau.enums import GameEvents, GameState
from mau.events import Event
from maubot import keyboards, messages
from maubot.config import sm, stickers
from maubot.events.journal import EventRouter, MessageChannel
from maubot.messages import plural_form

er = EventRouter()


@er.event(GameEvents.SESSION_START)
async def start_session(event: Event, chan: MessageChannel) -> None:
    """Отправляет лобби, когда начинается новая игра в чате."""
    lobby_message = (
        f"{messages.get_room_status(event.game)}\n\n"
        f"🔥 {event.player.name}, Начинает новую игру!"
    )
    await chan.send_lobby(
        message=lobby_message,
        reply_markup=keyboards.get_room_markup(event.game),
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
        message=messages.get_room_status(event.game),
        reply_markup=None,
    )
    await chan.clear()
    await chan.send_card(stickers.normal[event.game.deck.top.to_str()])
    chan.add(messages.get_new_game_message(event.game))
    await chan.send()


@er.event(GameEvents.GAME_END)
async def end_game(event: Event, chan: MessageChannel) -> None:
    """Завершает игру в чате."""
    sm.remove(event.game.room_id)
    chan.add(messages.end_game_message(event.game))
    chan.set_markup(keyboards.NEW_GAME_MARKUP)
    await chan.send()


@er.event(GameEvents.GAME_JOIN)
async def join_player(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if not event.game.started:
        lobby_message = (
            f"{messages.get_room_status(event.game)}\n\n"
            f"👋 {event.player.name} зашёл в комнату!"
        )
        await chan.send_lobby(
            message=lobby_message,
            reply_markup=keyboards.get_room_markup(event.game),
        )
        return

    chan.add(f"🍰 Добро пожаловать в игру, {event.player.name}!")
    await chan.send()


@er.event(GameEvents.GAME_LEAVE)
async def leave_player(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь вышел из игры."""
    if chan.lobby_message is not None and not event.game.started:
        lobby_message = (
            f"{messages.get_room_status(event.game)}\n\n"
            f"👋 {event.player.name} покинул комнату!"
        )
        await chan.send_lobby(
            message=lobby_message,
            reply_markup=keyboards.get_room_markup(event.game),
        )
        return

    if event.data == "win":
        chan.add(f"👑 {event.player.name} закончил(а)!\n")
    else:
        chan.add(f"👋 {event.player.name} покидает комнату.")

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
        f"🤝 {event.player.name} ({len(other_player.hand)} карт) "
        f"и {other_player.name} ({len(event.player.hand)} карт) "
        "обменялись картами.\n"
    )


@er.event(GameEvents.GAME_TURN)
async def next_turn(event: Event, chan: MessageChannel) -> None:
    """Начала следующего хода."""
    await chan.clear()
    cards = len(event.player.hand)
    chan.add(
        f"\n🍰 <b>ход</b>: {event.game.player.name} "
        f"(🃏 {cards} {plural_form(cards, ('карту', 'карты', 'карт'))})"
    )
    await chan.send()


@er.event(GameEvents.GAME_ROTATE)
async def rotate_cards(event: Event, chan: MessageChannel) -> None:
    """Все игрока обменялись картами, возвращает сколько карт у игроков."""
    chan.add("🌀 Обмениваемся <b>картами</b>!")
    chan.add(messages.get_room_players(event.game))


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
        chan.set_markup(keyboards.SHOTGUN_KEYBOARD)

    elif state == GameState.TWIST_HAND:
        chan.add("✨ С кем бы обменяться картами ..")
        chan.set_markup(keyboards.select_player_markup(event.game))

    elif state == GameState.CHOOSE_COLOR:
        chan.add("✨ Какой бы выбрать цвет ...")
        chan.set_markup(keyboards.SELECT_COLOR)

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
            f"🃏 {event.player.name} Берёт {event.data} "
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
        chan.add(f"🎩 {player.name} <b>Честный игрок</b>!")


@er.event(GameEvents.PLAYER_INTERVENED)
async def on_intervention(event: Event, chan: MessageChannel) -> None:
    """Когда игрок вмешивается в игру и перехватывает ход."""
    chan.add(f"⚡ {event.player.name} <b>навёл суеты!</b>")
    await chan.send()
