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

        self.twist_hand = Rule(self, 0, "🤝 Обмен картами")
        self.rotate_cards = Rule(self, 1, "🌀 Круговой обмен")
        self.one_winner = Rule(self, 2, "👑 Один победитель")
        self.auto_skip = Rule(self, 3, "💸 Авто пропуск")
        self.take_until_cover = Rule(self, 4, "🍷 Беру до последнего")
        self.shotgun = Rule(self, 5, "🔫 Револьвер")
        self.deferred_take = Rule(self, 6, "⏳ Отложенное взятие")
        self.auto_choose_color = Rule(self, 7, "🌷 самоцвет")
        self.random_color = Rule(self, 8, "🎲 Какой цвет")
        self.side_effect = Rule(self, 9, "💎 Побочный выброс")
        self.twist_hand_pass = Rule(self, 10, "👋 Без обмена")
        self.random_cards = Rule(self, 11, "🎰 Случайные карты")
        self.intervention = Rule(self, 12, "😈 Вмешательство 🔧")
        self.special_wild = Rule(self, 13, "❤️ Особая дикость")

    def iter_rules(self) -> Iterator[tuple[str, bool]]:
        """Возвращает итератор правил."""
        for rule in self.rules:
            yield (rule.name, (self.rule_flags & rule.index) != 0)

    def toggle(self, rule: int) -> None:
        """Переключает состояние битового флага."""
        self.rule_flags ^= 1 << rule
