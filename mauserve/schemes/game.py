"""Схемы, используемые во время игры."""

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel

from mau.card import (
    BaseCard,
    CardColor,
    CardType,
    ChooseColorCard,
    NumberCard,
    ReverseCard,
    TakeCard,
    TakeFourCard,
    TurnCard,
)
from mau.deck import Deck
from mau.enums import GameState
from mau.game import Rule, UnoGame
from mau.player import Player, SortedCards
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


class CardDeckData(BaseModel):
    """Информация о колоде карт.

    Предоставляет статистику сколько карт доступно и сколько уже
    использовано,
    """

    top: CardData
    cards: int
    used: int


class SortedCardsData(BaseModel):
    """Описание карт в руке игрока."""

    cover: list[CardData]
    uncover: list[CardData]


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
    name: str
    hand: int | SortedCardsData
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

    # Состояние комнаты
    deck: CardDeckData
    reverse: bool
    take_flag: bool
    take_counter: int
    shotgun_current: int
    state: GameState


@dataclass(slots=True)
class GameContext:
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


def card_to_data(card: BaseCard) -> CardData:
    """Преобразуем экземпляр карты в её схему."""
    return CardData(
        color=card.color,
        card_type=card.card_type,
        value=card.value,
    )


def deck_to_data(deck: Deck) -> CardDeckData:
    """Преобразует колоду карт в схему, оставляя только количество карт."""
    return CardDeckData(
        top=card_to_data(deck.top),
        cards=len(deck.cards),
        used=len(deck.used_cards),
    )


def sorted_cards_to_data(player_hand: SortedCards) -> SortedCardsData:
    """Перегоняет сортированные карты в схему."""
    return SortedCardsData(
        cover=[card_to_data(card) for card in player_hand.cover],
        uncover=[card_to_data(card) for card in player_hand.uncover],
    )


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
        name=player.name,
        hand=sorted_cards_to_data(player.get_cover_cards())
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
        take_flag=game.take_flag,
        take_counter=game.take_counter,
        shotgun_current=game.shotgun_current,
        state=game.state,
    )


async def context_to_data(ctx: GameContext) -> ContextData:
    """Преобразует игровой контекст в схему."""
    return ContextData(
        game=None if ctx.game is None else game_to_data(ctx.game),
        player=None
        if ctx.player is None
        else player_to_data(ctx.player, show_cards=True),
    )


def card_schema_to_card(card: CardData) -> BaseCard:
    """Возвращает карту из запакованных данных."""
    if card.card_type == CardType.NUMBER:
        return NumberCard(card.color, card.value)
    elif card.card_type == CardType.TAKE:
        return TakeCard(card.color, card.value)
    elif card.card_type == CardType.REVERSE:
        return ReverseCard(card.color)
    elif card.card_type == CardType.TURN:
        return TurnCard(card.color, card.value)
    elif card.card_type == CardType.CHOOSE_COLOR:
        return ChooseColorCard()
    elif card.card_type == CardType.TAKE_FOUR:
        return TakeFourCard(card.value)
