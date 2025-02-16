"""Схемы, используемые во время игры."""

from datetime import datetime
from typing import NamedTuple

from pydantic import BaseModel

from mau.card import BaseCard, CardColor, CardType
from mau.deck import Deck
from mau.game import Rule, UnoGame
from mau.player import Player
from mauserve.models import RoomModel, UserModel
from mauserve.schemes.roomlist import RoomMode


class CardData(BaseModel):
    """Сохраняет информацию о карте.

    Информация о картах является исчерпывающей.
    - цвет карты.
    - Тип карты.
    - Числовое значение.
    - Стоимость карты.
    """

    color: CardColor
    card_type: CardType
    value: int
    cost: int


class CardDeckData(BaseModel):
    """Информация о колоде карт.

    Предоставляет статистику сколько карт доступно и сколько уже
    использовано,
    """

    cards: int
    used: int


class PlayerData(BaseModel):
    """Информация об игроке.

    Используется при отображении всех игроков.
    Чтобы получить подробную информацию о пользователе. лучше
    воспользоваться методом получения пользователя из бд.

    - id пользователя.
    - Сколько карт у него вв руке.
    - Скольку раз стрелял из револьвера.

    также вместо количества карт может быть полное их описание.
    Только в том случае, если это игрок, запрашивающий данные о себе.
    """

    user_id: str
    hand: int | list[CardData]
    shotgun_current: int


class GameData(BaseModel):
    """Полная информация о состоянии игры."""

    # Информация о настройках комнаты
    room_id: str
    rules: list[RoomMode]
    owner_id: str
    game_started: datetime
    turn_started: datetime

    # Информация об игроках комнаты
    players: list[PlayerData]
    winners: list[PlayerData]
    losers: list[PlayerData]
    current_player: int

    # Состояние комнаты    pass

    deck: CardDeckData
    reverse: bool
    bluff_flag: bool
    take_flag: bool
    take_counter: int

    # Револьвер
    shotgun_current: int


class GameContext(NamedTuple):
    """Игровой контекст."""

    user: UserModel
    room: RoomModel
    game: UnoGame | None
    player: Player | None


class ContextData(BaseModel):
    """Отправляемая схема контекста."""

    game: GameData | None
    player: PlayerData | None


# конвертация моделей
# ===================


def card_to_model(card: BaseCard) -> CardData:
    """Преобразуем экземпляр карты в её схему."""
    return CardData(
        color=card.color,
        card_type=card.card_type,
        value=card.value,
        cost=card.cost,
    )


def deck_to_data(deck: Deck) -> CardDeckData:
    """Преобразует колоду карт в схему, оставляя только количество карт."""
    return CardDeckData(len(deck.cards), len(deck.used_cards))


def player_to_data(
    player: Player, show_cards: bool | None = False
) -> PlayerData:
    """Преобразует игрока в схему.

    Пропускает поле `shotgun_lose`, чтобы не подсматривали.
    Также если `show_cards` не установлен, отобразит только количество
    карт.
    """
    return PlayerData(
        user_id=player.user_id,
        hand=[card_to_model(card) for card in player.hand]
        if show_cards
        else len(player.hand),
        shotgun_current=player.shotgun_current,
    )


def rule_to_data(rule: Rule) -> RoomMode:
    """Преобразует игровое правило в схему."""
    return RoomMode(key=rule.key, name=rule.name, status=rule.status)


def game_to_data(game: UnoGame) -> GameData:
    """Преобразует игру в схему."""
    return GameData(
        room_id=game.room_id,
        rules=[rule_to_data(rule) for rule in game.rules],
        owner_id=game.owner.user_id,
        game_started=game.game_start,
        turn_started=game.turn_start,
        players=[player_to_data(player) for player in game.players],
        winners=[player_to_data(player) for player in game.winners],
        losers=[player_to_data(player) for player in game.losers],
        current_player=game.current_player,
        deck=deck_to_data(game.deck),
        reverse=game.reverse,
        bluff_flag=game.bluff_player,
        take_flag=game.take_flag,
        take_counter=game.take_counter,
        shotgun_current=game.shotgun_current,
    )


async def context_to_data(ctx: GameContext) -> ContextData:
    """Преобразует игровой контекст в схему."""
    return ContextData(
        game=None if ctx.game is None else game_to_data(ctx.game),
        player=None
        if ctx.player is None
        else player_to_data(ctx.player, show_cards=True),
    )
