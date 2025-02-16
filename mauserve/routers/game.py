"""Обработка игры."""

from fastapi import APIRouter, Depends, HTTPException

from mau.card import CardColor, TakeCard, TakeFourCard
from mau.enums import GameState
from mau.player import BaseUser
from mauserve.config import sm, stm
from mauserve.models import GameModel, RoomModel, UserModel
from mauserve.schemes.game import ContextData, GameContext, context_to_data

router = APIRouter(prefix="/game", tags=["games"])

# TODO: Тут будет не дурно систему оповещения сделать потом


async def get_context(user: UserModel = Depends(stm.read_token)) -> GameContext:
    """Получает игровой контекст пользователя.

    Контекст хранит в себе исчерпывающую информацию о состоянии игры.
    Актуальная информация об активном игроке.
    В какой комнате сейчас находится игрок.
    Если игрок не находится в комнате, вернётся ошибка.
    Также включат информацию об игре внутри комнаты и пользователя
    как игрока.
    """
    room = (
        await RoomModel.filter(players=user)
        .exclude(status="ended")
        .get_or_none()
    )
    if room is None:
        raise HTTPException(404, "user not in room, to join room game")

    game = sm.games.get(room.id)
    if game is not None:
        player = game.get_player(user.id)
    else:
        player = None

    return GameContext(user=user, room=room, game=game, player=player)


# Player routers
# ==============


@router.post("/join/")
async def join_player_to_game(
    ctx: GameContext = Depends(get_context),
) -> ContextData:
    """Добавляет активного пользователя в комнату.

    Под пользователем имеется ввиду активная учётная запись.
    Под комнатой предполагается текущая активная комната пользователя.
    """
    if ctx.game is None:
        raise HTTPException(404, "Room game not started to join")
    if ctx.player is not None:
        raise HTTPException(409, "Player already join to room")

    # TODO: Ошибки кто обрабатывать будет? А?
    sm.join(ctx.room.id, BaseUser(ctx.user.id, ctx.user.name))

    # TODO: Рассказываем всем в комнате что у нас новичок появился
    return await context_to_data(ctx)


@router.post("/leave")
async def leave_player_from_room(
    ctx: GameContext = Depends(get_context),
) -> ContextData:
    """Выходит из активной комнаты.

    Предполагается что прямо сейчас пользователь есть в игре.
    """
    if ctx.player is None or ctx.game is None:
        raise HTTPException(404, "Room or player not found to leave from game")

    sm.leave(ctx.player)
    # TODO: Сообщение в журнал что такой-то пользователь покинул нас
    if not ctx.game.started:
        await GameModel.create(
            create_time=ctx.game.game_start,
            owner_id=ctx.game.owner.user_id,
            room=ctx.room,
            winners_id=[pl.user_id for pl in ctx.game.winners],
            losers_id=[pl.user_id for pl in ctx.game.winners],
        )
        sm.remove(ctx.room.id)
    return await context_to_data(ctx)


# Session Routers
# ===============


@router.get("/")
async def get_context(ctx: GameContext = Depends(get_context)) -> ContextData:
    """Получает игровой контекст.

    Включает в себя данные о пользователе, комнате, текущей игре
    и игроке.
    может быть полезно чтобы обновить полную информацию о контексте.
    """
    return await context_to_data(ctx)


@router.post("/start")
async def start_room_game(
    ctx: GameContext = Depends(get_context),
) -> ContextData:
    """Начинает новую игру в комнате.

    Включает в себя как процесс создания комнаты, так и начало игры.
    """
    if ctx.game is not None:
        raise HTTPException(
            409, "Game already created, end game before create new"
        )
    elif ctx.user.id != ctx.room.owner_id:
        raise HTTPException(401, "You are not a room owner to create new game")

    ctx.game = sm.create(
        ctx.user.id,
        BaseUser(ctx.user.id, ctx.user.name),
    )

    # Сразу добавляем всех игроков из комнаты
    for user in ctx.room.players:
        sm.join(ctx.room.id, BaseUser(user.id, user.name))

    ctx.game.start()
    # TODO: Оповещение о начале игры тут должно быть

    return await context_to_data(ctx)


@router.post("/end")
async def end_room_game(ctx: GameContext = Depends(get_context)) -> ContextData:
    """Принудительно завершает игру в комнате.

    Редко используемая опция, тем не менее имеет место быть.
    """
    if ctx.game is None:
        raise HTTPException(404, "No active game to end")
    elif ctx.user.id != ctx.room.owner_id:
        raise HTTPException(401, "You are not a room owner to end this game")

    await GameModel.create(
        create_time=ctx.game.game_start,
        owner_id=ctx.game.owner.user_id,
        room=ctx.room,
        winners_id=[pl.user_id for pl in ctx.game.winners],
        losers_id=[pl.user_id for pl in ctx.game.winners],
    )
    sm.remove(ctx.game.room_id)
    # TODO: Оповещение о завершении игры
    return await context_to_data(ctx)


@router.post("/kick/{user_id}")
async def kick_player(
    user_id: str, ctx: GameContext = Depends(get_context)
) -> ContextData:
    """Исключает пользователя из игры.

    После пользователь сможет вернутся только как наблюдатель.
    """
    if ctx.game is None:
        raise HTTPException(404, "No active game to kick player")
    elif ctx.user.id != ctx.room.owner_id:
        raise HTTPException(401, "You are not a room owner to kik player")

    ctx.game.remove_player(user_id)
    # TODO: Уведомление что игрок был исключён
    if not ctx.game.started:
        await GameModel.create(
            create_time=ctx.game.game_start,
            owner_id=ctx.game.owner.user_id,
            room=ctx.room,
            winners_id=[pl.user_id for pl in ctx.game.winners],
            losers_id=[pl.user_id for pl in ctx.game.winners],
        )
        sm.remove(ctx.game.room_id)
        # TODO: Оповещение о завершении игры

    return await context_to_data(ctx)


@router.post("/skip")
async def skip_player(ctx: GameContext = Depends(get_context)) -> ContextData:
    """Пропускает игрока.

    Если к примеру игрок зазевался и не даёт продолжать игру.
    """
    if ctx.game is None:
        raise HTTPException(404, "No active game to skip player")

    ctx.game.take_counter += 1
    ctx.game.player.take_cards()
    # skip_player = ctx.game.player
    ctx.game.next_turn()
    # TODO: Оповещаем что игрок зазевался и пропустил свой ход

    return await context_to_data(ctx)


# Turn routers
# ============


@router.post("/next")
async def next_turn(ctx: GameContext = Depends(get_context)) -> ContextData:
    """Передает ход дальше.

    Есть такая вероятность что пользователи могут шалить, пропуская свой ход.
    Но поскольку цель сбросить свои карты, это мало вероятно.
    """
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")
    elif ctx.player != ctx.game.player:
        raise HTTPException(404, "It's not your turn to skip it.")

    ctx.game.next_turn()
    # TODO: Отправляем уведомление следующему игроку
    return await context_to_data(ctx)


@router.post("/take")
async def take_cards(ctx: GameContext = Depends(get_context)) -> ContextData:
    """Взятие карт.

    Игрок берёт количество карт, равное игровому счётчику.
    При режиме с револьвером будет предложено выстрелить или взять
    карты.

    Чтобы взять карты и отказаться от выстрела - `/shotgun/take`.
    """
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")

    await ctx.player.call_take_cards()
    # TODO: Оповещаем что вообще произошло
    # TODO: Может игроку надо из револьвера стрельнуть
    return await context_to_data(ctx)


@router.post("/shotgun/take")
async def shotgun_take_cards(
    ctx: GameContext = Depends(get_context),
) -> ContextData:
    """Взять карты, чтобы не стрелять.

    В случае, когда игрок решил что лучше взять карты, чем рисковать
    своей игрой.
    """
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")

    # TODO: Кто-то взял картишки
    ctx.player.take_cards()
    # TODO: Картишки кончились

    # TODO: Ну кто там ходит дальше
    if (
        isinstance(ctx.game.deck.top, TakeCard | TakeFourCard)
        and ctx.game.take_counter
    ):
        ctx.game.next_turn()

    return await context_to_data(ctx)


@router.post("/shotgun/shot")
async def shotgun_shot(ctx: GameContext = Depends(get_context)) -> ContextData:
    """Когда решил стрелять, лишь бы не брать карты."""
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")

    res = ctx.player.shotgun()
    if res:
        # TODO: прощайте, ребята
        sm.leave(ctx.player)
    else:
        ctx.game.take_counter = round(ctx.game.take_counter * 1.5)
        if ctx.game.player != ctx.player:
            ctx.game.set_current_player(ctx.player)
        ctx.game.next_turn()
        ctx.game.state = GameState.SHOTGUN

    # TODO: Кто там продолжает игру
    # TODO: Игра завершилась
    if not ctx.game.started:
        await GameModel.create(
            create_time=ctx.game.game_start,
            owner_id=ctx.game.owner.user_id,
            room=ctx.room,
            winners_id=[pl.user_id for pl in ctx.game.winners],
            losers_id=[pl.user_id for pl in ctx.game.winners],
        )
        sm.remove(ctx.game.room_id)

    return await context_to_data(ctx)


@router.post("/bluff")
async def bluff_player(ctx: GameContext = Depends(get_context)) -> ContextData:
    """Проверка игрока на честность."""
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")

    await ctx.player.call_bluff()

    # TODO: Какой-то результат деятельности имеется
    return await context_to_data(ctx)


@router.post("/color/{color}")
async def select_card_color(
    color: CardColor, ctx: GameContext = Depends(get_context)
) -> ContextData:
    """Выбирает цвет для карты выбор цвета или +4."""
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")

    ctx.game.choose_color(color)
    # TODO: Звуки суеты
    return await context_to_data(ctx)


@router.post("/player/{player}")
async def select_player(
    player: int, ctx: GameContext = Depends(get_context)
) -> ContextData:
    """Выбирает игрока, с кем можно обменяться картами."""
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")

    other_player = ctx.game.players[player]
    if ctx.game.state == GameState.TWIST_HAND:
        # TODO: Произошёл обмен картами
        player.twist_hand(other_player)

    return await context_to_data(ctx)


@router.post("/card/{card}")
async def pust_card_from_hand(
    card: str, ctx: GameContext = Depends(get_context)
) -> ContextData:
    """Разыгрывает карту из руки игрока."""
    if ctx.game is None:
        raise HTTPException(404, "No active game in room")
    elif ctx.player is None:
        raise HTTPException(404, "You are not a game player")

    ctx.game.process_turn(card, ctx.player)

    # TODO: что-то случилось после этого
    return await context_to_data(ctx)
