"""Работа с базой данных.

База данных используется для сохранения статистический ифнормации
об игроке.
"""

from tortoise import Model, fields


class User(Model):
    """База данных игрока.

    Используется при сборе статистической информации об играх.

    - id: Telegram User ID
    - stats (bool): Включён ли сбор игровой статистики для пользователя.
    - first_places: Количество первых мест в играх.
    - game_played: Сколько всего партий сыграно.
    - cards_played: Сколько всего карт разыграно.
    """

    id = fields.BigIntField(primary_key=True)
    first_places = fields.IntField(default=0)
    total_games = fields.IntField(default=0)
    cards_played = fields.IntField(default=0)
