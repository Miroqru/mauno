"""Игровые правила.

В зависимости от выбранных правил изменяться поведение игры.
"""

from collections.abc import Iterator


class Rule:
    """Игровое правило."""

    def __init__(self, rules: "GameRules", index: int, name: str) -> None:
        self.rules = rules
        self.index = 1 << index
        self.name = name

        self.rules.rules.append(self)

    @property
    def status(self) -> bool:
        """Проверяет, установлен ли битовый флаг."""
        return (self.rules.rule_flags & self.index) != 0


class GameRules:
    """битовые флаги игровых правил."""

    def __init__(self) -> None:
        self.rule_flags = 0
        self.rules: list[Rule] = []

        self.twist_hand = Rule(self, 0, "🤝 Обмен руками")
        self.rotate_cards = Rule(self, 1, "🧭 Обмен телами.")
        self.take_until_cover = Rule(self, 2, "🍷 Беру до последнего.")
        self.single_shotgun = Rule(self, 3, "🎲 Общий револьвер.")
        self.shotgun = Rule(self, 4, "🔫 Рулетка.")
        self.auto_choose_color = Rule(self, 5, "🃏 самоцвет")
        self.choose_random_color = Rule(self, 6, "🎨 Случайный цвет")
        self.random_color = Rule(self, 7, "🎨 Какой цвет дальше?")
        self.side_effect = Rule(self, 8, "🌀 Побочный выброс")
        self.intervention = Rule(self, 9, "😈 Вмешательство 🔧")
        self.twist_hand_pass = Rule(self, 10, "👋 Без обмена")
        self.one_winner = Rule(self, 11, "👑 Один победитель")
        self.auto_skip = Rule(self, 12, "💸 Авто пропуск")
        self.deferred_take = Rule(self, 13, "⏳ Отложенное взятие")

    def iter_rules(self) -> Iterator[tuple[str, bool]]:
        """Возвращает итератор правил."""
        for rule in self.rules:
            yield (rule.name, (self.rule_flags & rule.index) != 0)

    def toggle(self, rule: int) -> None:
        """Переключает состояние битового флага."""
        self.rule_flags ^= 1 << rule
