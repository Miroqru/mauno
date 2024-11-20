"""Все использованные сообщения в боте, доступные в общем доступе.

Разные обработчики могут получить доступ к данным сообщениям.
"""

from maubot.config import config
from maubot.uno.game import RULES, UnoGame

# Статические сообщения
# =====================

# Когда пользователь пишет сообщение /help
HELP_MESSAGE = (
    "🍰 <b>Три простых шага чтобы начать</b>:\n"
    "1. Добавьте бота в группу.\n"
    "2. В группе начните новую игру через /game или подключитесь через /join.\n"
    "3. Если вас двое и больше, начинайте игру при помощи /start!\n"
    "4. Введите <code>@mili_maubot</code> в чате или жмякните на "
    "<code>via @mili_maubot</code>.\n"
    "Здесь все ваши карты, а ещё кнопки чтобы взять карты и посмотреть или "
    "проверить текущее состояние игры.\n"
    "<b>Серые</b> карты вы пока не можете разыграть.\n"
    "Нажмите на один из стикеров, чтобы разыграть его.\n\n"
    "Игроки могут подключиться в любое время.\n"
    "Чтобы покинуть игру используйте /leave.\n"
    "Если игрок долго думает. его можно пропустить командой /skip.\n"
    "☕ О прочих командах можно узнать в <b>меню</b>.\n"
)

# Рассказывает об авторстве проекта и новостном канале
STATUS_MESSAGE = (
    "🌟 <b>Информация о боте</b>:\n\n"
    "<b>Maubot</b> - Telegram бот с открытым исходным кодом, предоставляющий "
    "пользователям играть в Uno в групповых чатах.\n"
    "Исходный код проекта доступен в "
    "<a href='https://codeberg.org/pentergust/maubot'>Codeberg</a>.\n"
    "Мы будем очень рады если вы внесёте свой вклад в развитие бота. 🍓\n\n"
    "Узнать о всех новостях проекта вы можете в Telegram канале "
    "<a href='https://t.me/mili_qlaster'>Salorhard</a>."
)

# Игровые комнаты ------------------------------------------------------

# Если в данном чате ещё не создано ни одной комнаты
NO_ROOM_MESSAGE = (
    "👀 В данном чате <b>нет игровой комнаты</b>.\n"
    "Создайте новую при помощи команды /game."
)

# Когда недостаточно игроков для продолжения игры
NOT_ENOUGH_PLAYERS = (
    f"🍰 <b>Недостаточно игроков</b> (минимум {config.min_players}) для "
    "игры.\n"
    "Воспользуйтесь командой /join чтобы присоединиться к игре."
)


# Динамические сообщения
#  =====================

def get_room_rules(game: UnoGame):
    """Получает включенные игровые правила для текущей комнаты."""
    rule_list = ""
    active_rules = 0
    for rule in RULES:
        status = getattr(game.rules, rule.key, False)
        if status:
            active_rules += 1
            rule_list += f"\n- {rule.name}"

    if active_rules == 0:
        return ""
    return f"🔥 Выбранные правила {active_rules}:{rule_list}"


def get_new_game_message(game: UnoGame) -> str:
    """Сообщение о выбранных режимах игры."""
    return (
        "🍰 Да начнётся <b>Новая игра!</b>!\n"
        f"И первым у нас ходит {game.player.user.mention_html()}\n"
        f"/close чтобы закрыть комнату от посторонних.\n{get_room_rules(game)}"
    )


def get_room_status(game: UnoGame, now_created: bool = False) -> str:
    """Отображает статус текущей комнаты."""
    if game.deck.top is None:
        top_card = ""
    else:
        top_card = f"🃏 <b>Последняя карта</b>: {game.deck.top}\n"

    # Собираем список игроков
    reverse_sim = "🔺" if game.reverse else "🔻"
    members_list = f"✨ Участники ({len(game.players)}{reverse_sim}):\n"
    for i, player in enumerate(game.players):
        if i == game.current_player:
            members_list += (
                f"- <b>{player.user.mention_html()}</b> "
                f"({len(player.hand)} карт)\n"
            )
        else:
            members_list += (
                f"- {player.user.mention_html()} "
                f"({len(player.hand)} карт)\n"
            )

    # Собираем итоговое сообщение
    return (
        f"☕ <b>Текущая комната</b> для игры.\n{top_card}"
        f"<b>Создал</b>: {game.start_player.mention_html()}\n\n{members_list}\n"
        f"{get_room_rules(game)}\n"
        "- /join чтобы присоединиться к игре\n"
        "- /start для начала веселья"
    )
