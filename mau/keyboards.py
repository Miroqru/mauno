"""Вспомогательный генератор событий."""

from typing import TYPE_CHECKING

from mau.journal import EventAction

if TYPE_CHECKING:
    from mau.game import UnoGame


def select_player_markup(game: "UnoGame") -> list[EventAction]:
    """Клавиатура для выбора игрока.

    Отображает имя игрока и сколько у него сейчас карт.
    """
    res = []

    for i, pl in enumerate(game.players):
        if i == game.current_player:
            continue
        res.append(
            EventAction(
                text=f"{pl.name} ({len(pl.hand)} карт)",
                callback_data=f"select_player:{i}",
            )
        )

    if game.rules.twist_hand_pass.status:
        res.append(EventAction(text="🍷 Пропустить", callback_data="pss"))

    return res
