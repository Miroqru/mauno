"""Маршрутизация событий от движка."""

from mau.enums import GameEvents, GameState
from maubot import keyboards, messages
from maubot.config import sm, stickers
from maubot.events.journal import EventContext, EventRouter
from maubot.messages import plural_form

er = EventRouter()


# Обработчик сессий
# =================


@er.handler(event=GameEvents.SESSION_START)
async def start_session(ctx: EventContext) -> None:
    """Отправляет лобби, когда начинается новая игра в чате."""
    lobby_message = (
        f"{messages.get_room_status(ctx.event.game)}\n\n"
        f"🔥 {ctx.event.player.name}, Начинает новую игру!"
    )
    await ctx.send_lobby(
        message=lobby_message,
        reply_markup=keyboards.get_room_markup(ctx.event.game),
    )


@er.handler(event=GameEvents.SESSION_END)
async def end_session(ctx: EventContext) -> None:
    """Очищает устаревший канал сообщений."""
    ctx.journal.remove_channel(ctx.event.game.room_id)


# Обработка событий игры
# ======================


@er.handler(event=GameEvents.GAME_START)
async def start_game(ctx: EventContext) -> None:
    """Оповещает о начале новой игры."""
    await ctx.send_lobby(
        message=messages.get_room_status(ctx.event.game),
        reply_markup=None,
    )
    await ctx.clear()
    await ctx.send_card(stickers.normal[ctx.event.game.deck.top.to_str()])
    ctx.add(messages.get_new_game_message(ctx.event.game))
    await ctx.send()


@er.handler(event=GameEvents.GAME_END)
async def end_game(ctx: EventContext) -> None:
    """Завершает игру в чате."""
    sm.remove(ctx.event.game.room_id)
    ctx.add(messages.end_game_message(ctx.event.game))
    ctx.set_markup(keyboards.NEW_GAME_MARKUP)
    await ctx.send()


@er.handler(event=GameEvents.GAME_JOIN)
async def join_player(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if not ctx.event.game.started:
        lobby_message = (
            f"{messages.get_room_status(ctx.event.game)}\n\n"
            f"👋 {ctx.event.player.name} зашёл в комнату!"
        )
        await ctx.send_lobby(
            message=lobby_message,
            reply_markup=keyboards.get_room_markup(ctx.event.game),
        )
        return

    ctx.add(f"🍰 Добро пожаловать в игру, {ctx.event.player.name}!")
    await ctx.send()


@er.handler(event=GameEvents.GAME_LEAVE)
async def leave_player(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if ctx._channel.lobby_message is not None and not ctx.event.game.started:
        lobby_message = (
            f"{messages.get_room_status(ctx.event.game)}\n\n"
            f"👋 {ctx.event.player.name} покинул комнату!"
        )
        await ctx.send_lobby(
            message=lobby_message,
            reply_markup=keyboards.get_room_markup(ctx.event.game),
        )
        return

    if ctx.event.data == "win":
        ctx.add(f"👑 {ctx.event.player.name} закончил(а)!\n")
    else:
        ctx.add(f"👋 {ctx.event.player.name} покидает комнату.")

    # Это может бывать выход из игры до её начала
    if not ctx.event.game.started:
        ctx.set_markup(None)

    await ctx.send()


@er.handler(event=GameEvents.GAME_SELECT_COLOR)
async def select_card_color(ctx: EventContext) -> None:
    """Какой новый цвет был выбран."""
    ctx.add(f"🎨 Я выбираю.. {ctx.event.data}!")


@er.handler(event=GameEvents.GAME_SELECT_PLAYER)
async def twist_hand(ctx: EventContext) -> None:
    """Сообщает об обмене картами между пользователями."""
    other_player = sm.player(ctx.event.data)
    if other_player is None:
        ctx.add("🍺 Куда подевался второй игрок?")
        return

    # Событие происходит после выполнения действия, потому так считаем карты
    ctx.add(
        f"🤝 {ctx.event.player.name} ({len(other_player.hand)} карт) "
        f"и {other_player.name} ({len(ctx.event.player.hand)} карт) "
        "обменялись картами.\n"
    )


@er.handler(event=GameEvents.GAME_TURN)
async def next_turn(ctx: EventContext) -> None:
    """Начала следующего хода."""
    await ctx.clear()
    cards = len(ctx.event.player.hand)
    ctx.add(
        f"\n🍰 <b>ход</b>: {ctx.event.game.player.name} "
        f"(🃏 {cards} {plural_form(cards, ('карту', 'карты', 'карт'))})"
    )
    await ctx.send()


@er.handler(event=GameEvents.GAME_ROTATE)
async def rotate_cards(ctx: EventContext) -> None:
    """Все игрока обменялись картами, возвращает статистику."""
    ctx.add("🌀 Обмениваемся <b>картами</b>!")
    ctx.add(messages.get_room_players(ctx.event.game))


@er.handler(event=GameEvents.GAME_STATE)
async def set_game_state(ctx: EventContext) -> None:
    """Изменение игрового состояния."""
    state = GameState(int(ctx.event.data))

    if state == GameState.SHOTGUN and (
        ctx.event.game.rules.shotgun.status
        or ctx.event.game.rules.single_shotgun.status
    ):
        current = (
            ctx.event.game.shotgun_current
            if ctx.event.game.rules.single_shotgun.status
            else ctx.event.player.shotgun_current
        )
        ctx.add(
            f"🍷 беру {ctx.event.game.take_counter} карт.\n"
            "💼 У нас для Вас есть <b>деловое предложение</b>!\n\n"
            f"Вы можете <b>взять свои карты</b> "
            "или же попробовать <b>выстрелить из револьвера</b>.\n"
            "Если вам повезёт, то карты будет брать уже следующий игрок.\n"
            f"🔫 Из револьвера стреляли {current} / 8 раз\n."
        )
        ctx.set_markup(keyboards.SHOTGUN_KEYBOARD)

    elif state == GameState.TWIST_HAND:
        ctx.add(f"✨ {ctx.event.player.name} Задумывается c кем обменяться.")
        ctx.set_markup(keyboards.select_player_markup(ctx.event.game))

    elif state == GameState.CHOOSE_COLOR:
        ctx.add(f"✨ {ctx.event.player.name} Задумывается о выборе цвета..")
        ctx.set_markup(keyboards.SELECT_COLOR)

    await ctx.send()


# Обработка действий игрока
# =========================


@er.handler(event=GameEvents.PLAYER_UNO)
async def say_uno(ctx: EventContext) -> None:
    """Оповещает что у игрока осталась одна карта."""
    ctx.add("\n🌟 <b>UNO!</b>")


@er.handler(event=GameEvents.PLAYER_TAKE)
async def player_take_cards(ctx: EventContext) -> None:
    """Оповещает что пользователь взял карты."""
    # Костыль, не трогать позязя
    if ctx._channel.lobby_message is None:
        ctx.add(
            f"🃏 {ctx.event.player.name} Берёт {ctx.event.data} "
            f"{plural_form(int(ctx.event.data), ('карту', 'карты', 'карт'))}"
        )
        await ctx.send()


@er.handler(event=GameEvents.PLAYER_BLUFF)
async def player_bluffing(ctx: EventContext) -> None:
    """Если изволите блефовать."""
    bluff_flag, take_counter = ctx.event.data.split(";")
    bluff_player = ctx.event.game.bluff_player
    if bluff_player is not None and bluff_flag == "true":
        ctx.add("🔎 <b>Замечен блеф</b>!")
    elif bluff_player is None:
        ctx.add("🎩 <b>Никто не блефовал</b>!")
    else:
        ctx.add(f"🎩 {bluff_player.name} <b>Честный игрок</b>!")


@er.handler(event=GameEvents.PLAYER_INTERVENED)
async def on_intervention(ctx: EventContext) -> None:
    """Если игрок вмешивается в игру и перехватывает ход."""
    ctx.add(f"⚡ {ctx.event.player.name} <b>навёл суеты!</b>")
    await ctx.send()
