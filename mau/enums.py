"""Перечисления для бота.

Здесь представлен общий перечень всех перечислений, используемых в игре.
Они представлены в одном месте для большего удобства.
А также для решения проблемы циклического импорта.
"""

from enum import StrEnum


class GameState(StrEnum):
    """Игровые состояния.

    Игровой процесс может находиться в нескольких игровых состояниях:

    - NEXT: После завершения действия игрока ход передаётся дальше.
    - CHOOSE_COLOR: Игрока разыграл чёрную карту и выбирает цвет.
    - TWIST_HAND: Игрок разыграл карту 2 и выбирает с кем обменяться.
    - SHOTGUN: Игрок выбирает, стоит ли ему стрелять из револьвера.
    - CONTINUE: Ход игрока продолжается после выполнения действия.

    Во всех состояниях, кроме NEXT, игра приостанавливается, пока
    вручную не будет указан переход до следующего хода.
    """

    NEXT = "next"
    CHOOSE_COLOR = "color"
    TWIST_HAND = "twist"
    SHOTGUN = "shotgun"
    CONTINUE = "continue"


class GameEvents(StrEnum):
    """Все варианты игровых событий.

    Типы событий могут сопровождаться уточняющими данными.

    Игровая сессия:
    - session_start: Началась новая сессия.
    - session_end: Закончилась сессия.
    - session_join: Игрок присоединился к сессии.
    - session_leave: Игрок покинул сессию.

    Игра:
    - game_start: Началась новая игра.
    - game_end: Игра завершилась.
    - game_join: Игрой зашёл в игру.
    - game_leave: Игрок вышел, проиграл, выиграл, был исключён, застрелился.
    - game_next: Переход к следующему игроку.
    - game_select_color: Выбор цвета для карты.
    - game_select_player: Выбор игрока для обмена картами.
    - game_turn: Переход к следующему ходу.
    - game_rotate: Обмен картами между всеми игроками.
    - game_uno: Крикнуть что осталась одна карта.
    - game_state: Обновление состояния игры.

    Игрок:
    - player_bluff: Проверка на честность прошлого игрока.
    - player_take: Взятие карт из колоды, также вместо револьвера.
    - player_push: Игрок выбросил карту.
    - player_intervened: Игрок вмешался во время игры.
    """

    # Игровые сессии
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SESSION_JOIN = "session_join"
    SESSION_LEAVE = "session_leave"

    # Игровые события
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_JOIN = "game_join"
    GAME_LEAVE = "game_leave"
    GAME_NEXT = "game_next"
    GAME_SELECT_COLOR = "game_select_color"
    GAME_SELECT_PLAYER = "game_select_player"
    GAME_TURN = "game_turn"
    GAME_ROTATE = "game_rotate"
    GAME_UNO = "game_uno"
    GAME_STATE = "game_state"

    # Игрок
    PLAYER_BLUFF = "player_bluff"
    PLAYER_TAKE = "player_take"
    PLAYER_PUSH = "player_push"
    PLAYER_INTERVENED = "player_intervened"
