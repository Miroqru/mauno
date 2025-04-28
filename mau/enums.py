"""Перечисления для бота.

Здесь представлен общий перечень всех перечислений, используемых в игре.
Они представлены в одном месте для большего удобства.
А также для решения проблемы циклического импорта.
"""

from enum import IntEnum


class GameState(IntEnum):
    """Игровые состояния.

    В зависимости от состояние изменяется поведение игры.

    - NEXT: После завершения действия игрока ход передаётся дальше.
    - TAKE: Игрок уже брал карту в этом ходу.
    - CHOOSE_COLOR: Игрок разыграл дикую карту и выбирает цвет.
    - TWIST_HAND: Игрок выбирает с кем обменяться картами.
    - SHOTGUN: Игрок выбирает, стоит ли ему стрелять из револьвера.
    - CONTINUE: Ход продолжается до ручного завершения.
    """

    NEXT = 0
    TAKE = 1
    CHOOSE_COLOR = 2
    TWIST_HAND = 3
    SHOTGUN = 4
    CONTINUE = 5


class GameEvents(IntEnum):
    """Все варианты игровых событий.

    Используется в обработчике для совершения действий на события.
    Некоторые события сопровождаются дополнительной информацией.

    Игровая сессия:
    - session_start: Создана новая комната.
    - session_end: Сессия в комнате завершена.

    Игра:
    - game_start: Началась новая игра.
    - game_end: Завершилась игра.
    - game_join: Игрок присоединился к игре.
    - game_leave: Игрок вышел, проиграл, выиграл, был исключён, застрелился.
    - game_select_color: Выбор нового цвета для карты.
    - game_select_player: Выбор игрока для обмена картами.
    - game_turn: Завершение текущего и начало следующего хода.
    - game_rotate: Обмен картами между всеми игроками.
    - game_state: Обновление игрового состояния.

    Игрок:
    - player_uno: Сообщить всем что у игрока осталась одна карта.
    - player_bluff: Проверка на честность предыдущего игрока.
    - player_take: Взятие карт из колоды, также вместо револьвера.
    - player_push: Игрок использует карту.
    - player_intervened: Игрок вмешался в ход другого игрока.
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

    PLAYER_UNO = 30
    PLAYER_BLUFF = 31
    PLAYER_TAKE = 32
    PLAYER_PUSH = 33
    PLAYER_INTERVENED = 34


# Emoji для представления цвета карты
COLOR_EMOJI = ["❤️", "💛", "💚", "💙", "🖤"]
CARD_TYPES = ["", "skip", "reverse", "take", "color", "take_four"]


class CardColor(IntEnum):
    """Все доступные цвета карт UNO."""

    RED = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3
    BLACK = 4

    def __str__(self) -> str:
        """Представление цвета в виде смайлика."""
        return COLOR_EMOJI[self.value]


class CardType(IntEnum):
    """Основные типы карт UNO.

    - NUMBER: Числа от 0 до 9.
    - TURN: Пропуск хода следующего игрока.
    - REVERSE: Переворачивает очередь ходов.
    - TAKE: Следующий игрок берёт карты.
    - CHOOSE_COLOR: Выбирает любой цвет для карты.
    - TAKE_FOUR: Выбирает цвет, даёт +4 карты следующему игроку.
    """

    NUMBER = 0
    TURN = 1
    REVERSE = 2
    TAKE = 3
    CHOOSE_COLOR = 4
    TAKE_FOUR = 5

    def __str__(self) -> str:
        """Представление тип карты одним словом."""
        return CARD_TYPES[self.value]

    @property
    def cost(self) -> int:
        """Подсчитывает стоимость карты на основе её типа."""
        if self in (CardType.TAKE_FOUR, CardType.CHOOSE_COLOR):
            return 50
        elif self == CardType.NUMBER:
            return 0
        else:
            return 20
