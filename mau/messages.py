"""общие сообщения.

Данные сообщения также используются внутри класса игры.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.game import UnoGame


def end_game_message(game: "UnoGame") -> str:
    """Сообщение об окончании игры.

    Отображает список победителей текущей комнаты и проигравших.
    Ну и полезные команды, если будет нужно создать новую игру.
    """
    res = "✨ <b>Игра завершилась</b>!\n"
    for i, winner in enumerate(game.winners):
        res += f"{i + 1}. {winner.name}\n"
    res += "\n👀 Проигравшие:\n"
    for i, loser in enumerate(game.losers):
        res += f"{i + 1}. {loser.name}\n"

    res += "\n🍰 /game - чтобы создать новую комнату!"
    return res


def get_room_players(game: "UnoGame") -> str:
    """Собирает список игроков для текущей комнаты.

    Отображает порядок хода, список всех игроков.
    Активного игрока помечает жирным шрифтом.
    Также указывает количество карт и выстрелов из револьвера.
    """
    reverse_sim = "🔺" if game.reverse else "🔻"
    players_list = f"✨ Игроки ({len(game.players)}{reverse_sim}):\n"
    for i, player in enumerate(game.players):
        if game.rules.shotgun.status:
            shotgun_stat = f" {player.shotgun_current} / 8 🔫"
        else:
            shotgun_stat = ""

        if i == game.current_player:
            players_list += (
                f"- <b>{player.name}</b> 🃏{len(player.hand)} {shotgun_stat}\n"
            )
        else:
            players_list += (
                f"- {player.name} 🃏{len(player.hand)} {shotgun_stat}\n"
            )
    return players_list
