"""Общие перечисления.

Перечисления представлены в одном место для большего удобства.
А также для решения проблемы циклического импорта.
"""

from enum import IntEnum

# Emoji для представления цвета карты
COLOR_EMOJI = ["❤️", "🧡", "💛", "💚", "🩵", "💙", "🖤", "🩷"]


class CardColor(IntEnum):
    """Цвета карты.

    У каждой карты есть свой цвет.
    Возможные варианты: `RED`, `YELLOW`, `GREEN`, `BLUE`, `BLACK`.
    Чёрный цвет используется для диких карт.
    Во время использования такой карты пользователю будет предложено
    выбрать один из доступных цветов, кроме чёрного.
    """

    RED = 0
    ORANGE = 1
    YELLOW = 2
    GREEN = 3
    CYAN = 4
    BLUE = 5
    BLACK = 6
    CREAM = 7

    @property
    def emoji(self) -> str:
        """Преобразует цвет карты в соответствующий emoji."""
        return COLOR_EMOJI[self.value]


class GameEvents(IntEnum):
    """Типы игровых событий.

    Когда происходит некоторое действие в игре, вызывается событие.
    События могут сопровождаться строкой с полезной информацией.
    Для обработки игровых события воспользуйтесь классом `EventHandler`.

    **Игровая сессия**:

    - `session_start`: Создана новая комната.
    - `session_end`: Сессия в комнате завершена.

    **Игра**:

    - `game_start`: Началась новая игра.
    - `game_end`: Завершилась игра.
    - `game_join`: Игрок присоединился к игре.
    - `game_leave`: Игрок вышел, проиграл, выиграл, был исключён, застрелился.
    - `game_select_color`: Выбор нового цвета для карты.
    - `game_select_player`: Выбор игрока для обмена картами.
    - `game_turn`: Завершение текущего и начало следующего хода.
    - `game_rotate`: Обмен картами между всеми игроками.
    - `game_state`: Обновление игрового состояния.

    **Игрок**:

    - `player_mau`: Когда у игрока остаётся только одна карта.
    - `player_bluff`: Проверка на честность предыдущего игрока.
    - `player_take`: Взятие карт из колоды, также вместо револьвера.
    - `player_put`: Игрок использует карту.
    - `player_intervened`: Игрок вмешался в ход другого игрока.
    """

    SESSION_START = 10
    SESSION_END = 11

    GAME_START = 20
    GAME_END = 21
    GAME_JOIN = 22
    GAME_LEAVE = 23
    GAME_SELECT_COLOR = 24
    GAME_SELECT_PLAYER = 25
    GAME_TURN = 26
    GAME_ROTATE = 27
    GAME_STATE = 28

    PLAYER_MAU = 30
    PLAYER_BLUFF = 31
    PLAYER_TAKE = 32
    PLAYER_PUT = 33
    PLAYER_INTERVENED = 34


class GameState(IntEnum):
    """Игровые состояния.

    В каждый момент времени игра находится в некотором состоянии.
    В зависимости от этого состояние изменяется поведение игры.
    Отслеживать состояния можно при помощи событий.
    Состояние игры сбрасывается на каждом ходе.

    - `NEXT`: После использования карты игроком ход передаётся дальше.
    - `TAKE`: Игрок брал карту в этом ходу.
    - `CHOOSE_COLOR`: Выбирается цвет для карты. После завершается ход.
    - `TWIST_HAND`: Выбирается с кем обменяться картами.
    - `SHOTGUN`: Состояние револьвера. Стрелять или брать карты.
    - `CONTINUE`: Ход продолжается до ручного завершения.
    """

    NEXT = 0
    TAKE = 1
    CHOOSE_COLOR = 2
    TWIST_HAND = 3
    SHOTGUN = 4
    CONTINUE = 5
