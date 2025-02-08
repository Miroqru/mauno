"""Информация об игровых режимах."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rule:
    """Правило для игры."""

    key: str
    name: str


RULES = (
    Rule("twist_hand", "🤝 Обмен руками"),
    Rule("rotate_cards", "🧭 Обмен телами."),
    Rule("take_until_cover", "🍷 Беру до последнего."),
    Rule("single_shotgun", "🎲 Общий револьвер."),
    Rule("shotgun", "🔫 Рулетка."),
    Rule("wild", "🐉 Дикие карты"),
    Rule("auto_choose_color", "🃏 самоцвет"),
    Rule("choose_random_color", "🎨 Случайный цвет"),
    Rule("random_color", "🎨 Какой цвет дальше?"),
    Rule("debug_cards", "🦝 Отладочные карты!"),
    Rule("side_effect", "🌀 Побочный выброс"),
    Rule("ahead_of_curve", "🔪 На опережение 🔧"),
    Rule("intervention", "😈 Вмешательство 🔧"),
)
