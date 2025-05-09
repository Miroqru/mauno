import requests
from icecream import ic

from mau.deck.presets import DeckGenerator

card_gen = DeckGenerator.from_preset("classic")

for card in card_gen._cards():
    card_str = card.pack()
    res = requests.get(f"http://127.0.0.1:8000/card/{card_str}/false")
    res.raise_for_status()
    ic(res)
