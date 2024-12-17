from random import choice, randint, random
from typing import TYPE_CHECKING, Self

from loguru import logger

from maubot.uno.card import BaseCard, CardColor, CardType
from maubot.uno.enums import GameState
from maubot.uno.player import Player

if TYPE_CHECKING:
    from maubot.uno.game import UnoGame


class Automa(Player):
    def __init__(self, game: 'UnoGame', bot_name, user=None):
        super().__init__(game, user)
        self.bot_name = bot_name

    @property
    def name(self) -> str:
        """Отображает имя игрока."""
        name = self.bot_name if self.user is None else self.ser.first_name
        return name + ' [🔧]'

    def select_random_card(self) -> BaseCard | None:
        cards = self.get_cover_cards()
        if not len(cards.cover):
            return None
        return choice(cards.cover)

    async def auto_turn(self):
        self.game.journal.set_markup(None)
        self.game.journal.add("✨ Выполняю автоматический ход")
        if self.game.deck.top.card_type == CardType.TAKE_FOUR:
            if random() > 0.5:
                self.game.journal.add("✨ Я думаю ты блефуешь!")
                self.simulate_bluff()
            else:
                self.game.journal.add("✨ Просто возьму карты..")
                self.simulate_take()

                if self.game.state == GameState.SHOTGUN:
                    self.simulate_shotgun()
                    await self.game.journal.send_journal()
                    await self.game.next_turn()

            await self.game.next_turn()
            await self.game.journal.send_journal()

        card = self.select_random_card()
        if card is None:
            self.game.journal.add("✨ Подходящей карты не нашлось")
            skip_flag  = self.simulate_take()
            if skip_flag:
                await self.game.journal.send_journal()
                await self.game.next_turn()
            elif self.game.state == GameState.SHOTGUN:
                self.simulate_shotgun()
                await self.game.journal.send_journal()
                await self.game.next_turn()
            else:
                card = self.select_random_card()
                if card is None:
                    await self.game.journal.send_journal()
                    await self.game.next_turn()
                else:
                    self.game.journal.add(f"✨ Разыгрываю карту {card}")
                    await self.game.journal.send_journal()
                    await self.simulate_play_card(card)
                    if self.game.state == GameState.CHOOSE_COLOR:
                        color = CardColor(randint(1, 4))
                        self.game.journal.add(f"✨ Выбираю цвет {color}")
                        await self.game.journal.send_journal()
                        await self.game.choose_color(color)
            
                    self.game.journal.add("✨ Ход окончен")
                    self.game.journal.add(f"✨ Дальше ходит {self.game.player.name}")
                    await self.game.journal.send_journal()
        else:
            self.game.journal.add(f"✨ Разыгрываю карту {card}")
            await self.game.journal.send_journal()
            await self.simulate_play_card(card)
            if self.game.state == GameState.CHOOSE_COLOR:
                color = CardColor(randint(1, 4))
                self.game.journal.add(f"✨ Выбираю цвет {color}")
                await self.game.journal.send_journal()
                await self.game.choose_color(color)
      
            self.game.journal.add("✨ Ход окончен")
            self.game.journal.add(f"✨ Дальше ходит {self.game.player.name}")
            await self.game.journal.send_journal()

    def __eq__(self, other_player: Self) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        if isinstance(other_player, Player):
            return False
        return self.bot_name == other_player.name

    def __ne__(self, other_player: Self) -> bool:
        """Проверяет что игроки не совпадают."""
        if isinstance(other_player, Player):
            return True
        return self.bot_name != other_player.user.id

    # Симуляция действий игрока
    # ==========================

    def select_player(self):
        pass

    def simulate_take(self) -> bool:
        if self.game.rules.take_until_cover and self.game.take_counter == 0:
            self.game.take_counter = self.game.deck.count_until_cover()
            self.game.journal.add(f"🍷 беру {self.game.take_counter} карт.\n")

        if not self.game.rules.shotgun and not self.game.rules.single_shotgun:
            return self.simulate_take_card()

        elif self.game.take_counter <= 2 or self.game.state == GameState.SHOTGUN:
            return self.simulate_take_card()

        current = (
            self.game.shotgun_current if self.game.rules.single_shotgun
            else self.shotgun_current
        )
        self.game.journal.add((
            "💼 У нас для Вас есть <b>деловое предложение</b>!\n\n"
            f"Вы можете <b>взять свои карты</b> "
            "или же попробовать <b>выстрелить из револьвера</b>.\n"
            "Если вам повезёт, то карты будет брать уже следующий игрок.\n"
            f"🔫 Из револьвера стреляли {current} / 8 раз\n."
        ))
        self.game.state = GameState.SHOTGUN

    def simulate_take_card(self: Player) -> bool:
        """Действие при взятии карты пользователем."""
        logger.info("{} take cards", self)
        take_counter = self.game.take_counter
        self.take_cards()
        if len(self.game.deck.cards) == 0:
            self.game.journal.add("🃏 В колоде не осталось карт для игрока.")

        # Если пользователь выбрал взять карты, то он пропускает свой ход
        if self.game.deck.top.card_type in (CardType.TAKE, CardType.TAKE_FOUR) and take_counter:
            return True
        return False

    def simulate__bluff(self: Player) -> str:
        """Проверка на честность предыдущего игрока."""
        logger.info("{} call bluff", self)
        bluff_player = self.game.bluff_player
        if bluff_player.bluffing:
            self.game.journal.add((
                "🔎 <b>Замечен блеф</b>!\n"
                f"{bluff_player.user.first_name} получает "
                f"{self.game.take_counter} карт."
            ))
            bluff_player.take_cards()

            if len(self.game.deck.cards) == 0:
                self.game.journal.add("🃏 В колоде не осталось свободных карт.")
        else:
            self.game.take_counter += 2
            self.game.journal.add((
                f"🎩 {bluff_player.user.first_name} <b>Честный игрок</b>!\n"
                f"{self.user.first_name} получает "
                f"{self.game.take_counter} карт.\n"
            ))
            self.take_cards()
            if len(self.game.deck.cards) == 0:
                self.game.journal.add("🃏 В колоде не осталось свободных карт.")

    async def simulate_play_card(self: Player, card: BaseCard) -> str:
        """Разыгрывает выброшенную карту."""
        logger.info("Push {} from {}", card, self.bot_name)
        self.hand.remove(card)
        await self.game.process_turn(card)
        self.game.journal.set_markup(None)

        if len(self.hand) == 1:
            self.game.journal.add("🌟 UNO!\n")

        if len(self.hand) == 0:
            self.game.journal.add(f"👑 {self.user.first_name} победил(а)!\n")
            self.game.winners.append(self)
            await self.game.remove_player(self.bot_name)

            if not self.game.started:
                self.game.journal.add(messages.end_game_message(self.game))

        elif card.cost == 2 and self.game.rules.twist_hand:
            self.game.journal.add(
                f"✨ {self.bot_name} Задумывается c кем обменяться."
            )
            self.game.journal.set_markup(keyboards.select_player_markup(player))

        elif (self.game.rules.rotate_cards
            and self.game.deck.top.cost == 0
            and len(self.hand) > 0
        ):
            self.game.journal.add((
                "🤝 Все игроки обменялись картами по кругу.\n"
                f"{messages.get_room_players(self.game)}"
            ))

        if card.card_type in (
            CardType.TAKE_FOUR, CardType.CHOOSE_COLOR
        ):
            self.game.journal.add(
                f"✨ {self.bot_name} Задумывается о выборе цвета."
            )

        if (self.game.rules.random_color
            or self.game.rules.choose_random_color
            or self.game.rules.auto_choose_color
        ):
            self.game.journal.add(
                f"🎨 Я выбираю цвет.. {self.game.deck.top.color}"
            )

