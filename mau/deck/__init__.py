"""Компоненты колоды карт.

Карты Mau - основной игроков элемент.
Именно ими играют игроки.

Поставляет следующие компоненты:
- Поведение дяя карт.
- Игровые карты.
- Коллекцию колоды карт.
- Заготовленные шаблоны для генерации колоды.
"""

# Пере использование часто используемых компонентов
from mau.deck.behavior import CardBehavior as CardBehavior

# Реализация карты
from mau.deck.card import CardColor as CardColor
from mau.deck.card import MauCard as MauCard

# Реализация колоды с картами
from mau.deck.deck import Deck as Deck
from mau.deck.deck import RandomDeck as RandomDeck
