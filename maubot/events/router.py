"""Маршрутизация событий от движка."""

from mau.enums import GameEvents
from maubot import keyboards, messages
from maubot.config import sm, stickers
from maubot.events.journal import EventContext, EventRouter
from maubot.messages import plural_form

er = EventRouter()


# Обработчик сессий
# =================


@er.handler(event=GameEvents.SESSION_START)
async def start_session(ctx: EventContext) -> None:
    """Отправляет лобби, когда начинается новая сессия в чате."""
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
    ctx.journal.remove_channel(ctx.event.room_id)


# Обработка событий игры
# ======================


@er.handler(event=GameEvents.GAME_JOIN)
async def join_player(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if ctx.event.game.started:
        ctx.add(f"🍰 Добро пожаловать в игру, {ctx.event.player.name}!")
        await ctx.send()
    else:
        lobby_message = (
            f"{messages.get_room_status(ctx.event.game)}\n\n"
            f"👋 {ctx.event.player.name}, добро пожаловать в комнату!"
        )
        await ctx.send_lobby(
            message=lobby_message,
            reply_markup=keyboards.get_room_markup(ctx.event.game),
        )


@er.handler(event=GameEvents.GAME_LEAVE)
async def leave_player(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    # Это может бывать выход из игры до её начала
    if ctx.event.data == "win":
        ctx.add(f"👑 {ctx.event.player.name} победил(а)!\n")
    else:
        ctx.add(f"👋 {ctx.event.player.name} покидает игру!\n")

    if not ctx.event.game.started:
        ctx.set_markup(None)

    await ctx.send()


@er.handler(event=GameEvents.GAME_UNO)
async def say_uno(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.add("🌟 UNO!\n")
    await ctx.send()


@er.handler(event=GameEvents.PLAYER_TAKE)
async def player_take_cards(ctx: EventContext) -> None:
    """Оповещает что пользователь взял N карт."""
    if not ctx._channel.lobby_message:
        ctx.add(
            f"🃏 {ctx.event.player.name} Берёт {ctx.event.data} "
            f"{plural_form(int(ctx.event.data), ('карту', 'карты', 'карт'))}"
        )
        await ctx.send()


@er.handler(event=GameEvents.GAME_ROTATE)
async def rotate_cards(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.add("🌀 Обмениваемся ручками")
    ctx.add(messages.get_room_players(ctx.event.game))
    await ctx.send()


@er.handler(event=GameEvents.GAME_SELECT_COLOR)
async def select_card_color(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.add(f"🎨 Я выбираю.. {ctx.event.data}!")
    await ctx.send()


@er.handler(event=GameEvents.GAME_START)
async def start_game(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    sticker = stickers.normal[ctx.event.game.deck.top.to_str()]
    await ctx.send_card(sticker)
    await ctx.send_message(messages.get_new_game_message(ctx.event.game))


@er.handler(event=GameEvents.GAME_END)
async def end_game(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.add(messages.end_game_message(ctx.event.game))
    ctx.set_markup(None)
    sm.remove(ctx.event.room_id)
    await ctx.send()


@er.handler(event=GameEvents.GAME_SELECT_PLAYER)
async def twist_hand(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    other_player = ctx.event.game.get_player(ctx.event.data)
    if other_player is None:
        ctx.add("🍺 Куда подевался второй игрок?")
    else:
        ctx.add(
            f"🤝 {ctx.event.player.name} ({len(other_player.hand)} карт) "
            f"и {other_player.name} ({len(ctx.event.player.hand)} карт) "
            "обменялись руками.\n"
        )
    await ctx.send()


@er.handler(event=GameEvents.PLAYER_BLUFF)
async def player_bluffing(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    bluff_flag, take_counter = ctx.event.data.split(";")
    bluff_player = ctx.event.game.bluff_player
    if bluff_player is not None and bluff_flag == "true":
        ctx.add(
            "🔎 <b>Замечен блеф</b>!\n"
            f"{bluff_player.name} получает "
            f"{take_counter} карт."
        )
    else:
        if bluff_player is None:
            bluff_header = "🎩 <b>Никто не блефовал</b>!\n"
        else:
            bluff_header = f"🎩 {bluff_player.name} <b>Честный игрок</b>!\n"

        name = ctx.event.player.name
        ctx.add(f"{bluff_header}{name} получает {take_counter} карт.\n")

    await ctx.send()


@er.handler(event=GameEvents.GAME_STATE)
async def set_game_state(ctx: EventContext) -> None:
    """Изменение игрового состояния."""
    if ctx.event.data == "shotgun" and (
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

    elif ctx.event.data == "twist_hand":
        ctx.add(f"✨ {ctx.event.player.name} Задумывается c кем обменяться.")
        ctx.set_markup(keyboards.select_player_markup(ctx.event.game))

    elif ctx.event.data == "choose_color":
        ctx.add(f"✨ {ctx.event.player.name} Задумывается о выборе цвета..")
        ctx.set_markup(keyboards.SELECT_COLOR)

    await ctx.send()


@er.handler(event=GameEvents.GAME_TURN)
async def next_turn(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    await ctx.clear()
    cards = len(ctx.event.player.hand)
    ctx.add(
        f"\n🍰 <b>ход</b>: {ctx.event.game.player.name} "
        f"(🃏 {cards} {plural_form(cards, ('карту', 'карты', 'карт'))})"
    )
    await ctx.send()
