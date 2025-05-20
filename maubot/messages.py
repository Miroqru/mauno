"""Все использованные сообщения в боте, доступные в общем доступе.

Разные обработчики могут получить доступ к данным сообщениям.
Здесь представлены как статические сообщения, так и динамические.
"""

from datetime import datetime

from mau.deck.card import MauCard
from mau.game.game import MauGame
from mau.game.player_manager import PlayerManager

_MEDALS = ("🥇", "🥈", "🥉")


def place_medal(i: int) -> str | None:
    """Возвращает медаль за место в рейтинге."""
    return _MEDALS[i] if i < len(_MEDALS) else None


def plural_form(n: int, v: tuple[str, str, str]) -> str:
    """Возвращает склонённое значение в зависимости от числа.

    Возвращает склонённое слово: "для одного", "для двух",
    "для пяти" значений.
    """
    return v[2 if (4 < n % 100 < 20) else (2, 0, 1, 1, 1, 2)[min(n % 10, 5)]]  # noqa: PLR2004


def time_delta(seconds: int) -> str:
    """Возвращает строковое представление времени из количества секунд.

    Модификатор времени автоматически склоняется в зависимости от времени.
    """
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    res = ""

    if h != 0:
        res += f"{m} {plural_form(m, ('час', 'часа', 'часов'))} "
    if m != 0:
        res += f"{m} {plural_form(m, ('минуту', 'минуты', 'минут'))} "
    if s != 0:
        res += f"{s} {plural_form(m, ('секунду', 'секунды', 'секунд'))}"
    return res


def game_rules_list(game: MauGame) -> str:
    """Получает включенные игровые правила для текущей комнаты.

    Отображает список правил и общее количество включенных правил.
    Если ничего не выбрано, то вернёт пустую строку.
    """
    rule_list = ""
    for name, status in game.rules.iter_rules():
        if status:
            rule_list += f"- {name}\n"
    return f"🪄 Игровые правила\n:{rule_list}" if rule_list != "" else ""


def players_list(pm: PlayerManager, reverse: bool, shotgun: bool) -> str:
    """Список игроков для текущей комнаты.

    Отображает порядок хода, список всех игроков.
    Активного игрока помечает жирным шрифтом.
    Также указывает количество карт и выстрелов из револьвера.
    """
    reverse_sim = "◀️" if reverse else "▶️"
    res = f"✨ Игроки {reverse_sim}:\n"
    for i, player in enumerate(pm.iter()):
        shotgun_stat = f" {player.shotgun.cur} / 8 🔫" if shotgun else ""
        name = (
            f"<b>{player.mention}</b>"
            if player == pm.current
            else player.mention
        )
        res += f"- {name} 🃏{len(player.hand)} {shotgun_stat}\n"
    return res


def _card_info(card: MauCard) -> str:
    return f"{card.color.emoji} {card.value} {card.behavior.name}"


def game_status(game: MauGame) -> str:
    """Возвращает статус текущей игры.

    Используется и при создании новой комнаты.
    Показывает список игроков и полезные команды.

    Если игра уже началась, то добавляется самая разна полезная
    информация о текущем состоянии игры.
    Как минимум список игроков, выбранные режимы, количество карт и так
    далее.
    """
    if not game.started:
        room_players = ", ".join(pl.mention for pl in game.pm.iter())
        return (
            f"☕ <b>Игровая комната</b> {game.owner.mention}!\n"
            f"✨ всего игроков {len(game.pm)}:\n{room_players}\n\n"
            "🪄 Игровые <b>правила</b> позволяют сделать игру более весёлой.\n"
            "🍉 Время присоединиться к игре!"
        )

    if game.rules.single_shotgun.status:
        shotgun_stats = f"🔫 <b>Револьвер</b>: {game.shotgun.cur} / 8"
    else:
        shotgun_stats = ""

    now = datetime.now()
    game_delta = time_delta(int((now - game.game_start).total_seconds()))
    turn_delta = time_delta(int((now - game.turn_start).total_seconds()))
    return (
        f"☕ <b>Игровая комната</b> {game.owner.name}:\n"
        f"🃏 <b>Последняя карта</b>: {_card_info(game.deck.top)}\n"
        f"🦝 <b>Ход</b> {game.player.mention}, прошло {turn_delta}\n"
        f"⏳ <b>Игра идёт</b> {game_delta}\n\n"
        f"{players_list(game.pm, game.reverse, game.rules.shotgun.status)}\n"
        f"{game_rules_list(game)}"
        f"📦 <b>карт</b> в колоде: {len(game.deck.cards)} доступно / "
        f"{len(game.deck.used_cards)} использовано.\n{shotgun_stats}"
    )


def end_game_players(pm: PlayerManager) -> str:
    """Сообщение об окончании игры.

    Содержит список победителей и проигравших.
    """
    res = "🎉 <b>Игра завершилась</b>!\n"
    for i, winner in enumerate(pm.iter(pm.winners)):
        res += f"{place_medal(i) or f'{i + 1}'}. {winner.name}\n"
    losers = sorted(
        [(p, p.count_cost()) for p in pm.iter(pm.losers)],
        key=lambda r: r[1],
        reverse=True,
    )

    res += "\n🎀 Проигравшие:\n"
    for i, loser in enumerate(losers):
        res += f"{i + 1}. {loser[0].name} - {loser[1]}✨\n"
    return res
