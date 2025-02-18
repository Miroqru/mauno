<script setup lang="ts">
import type { GameContext } from '@/share/api/types'
import { CardType, GameState } from '@/share/api/types'
import { computed } from 'vue'
import BluffButton from './buttons/BluffButton.vue'
import ColorButton from './buttons/ColorButton.vue'
import NextTurn from './buttons/NextTurn.vue'
import PlayerButton from './buttons/PlayerButton.vue'
import ShotButton from './buttons/ShotButton.vue'
import TakeCards from './buttons/TakeCards.vue'

const { context } = defineProps<{ context: GameContext }>()

const isYouTurn = computed(
  () => context.player?.user_id == context.game?.players[context.game.current_player].user_id,
)

const isCanBluffing = computed(
  () => context.game?.take_counter && context.game.deck.top.card_type == CardType.TAKE_FOUR,
)
</script>

<template>
  <section v-if="context.game && context.player" class="flex justify-around gap-4 my-4">
    <div v-if="isYouTurn">
      <!-- Выбираем цвет для карты -->
      <div
        v-if="context.game.state == GameState.CHOOSE_COLOR"
        class="flex flex-wrap justify-around gap-2 border-2 border-stone-700 rounded-md"
      >
        <ColorButton :color="0" color-name="красный" />
        <ColorButton :color="1" color-name="жёлтый" />
        <ColorButton :color="2" color-name="зелёный" />
        <ColorButton :color="3" color-name="синий" />
      </div>

      <!-- выбираем игрока для обмена руками -->
      <div
        v-if="context.game.state == GameState.TWIST_HAND"
        class="flex flex-wrap justify-around gap-2 border-2 border-stone-700 rounded-md"
      >
        <PlayerButton
          v-for="player in context.game.players"
          :key="player.user_id"
          :player="player"
        />
      </div>

      <div
        v-if="context.game.state == GameState.SHOTGUN"
        class="flex flex-wrap justify-around gap-2 border-2 border-stone-700 rounded-md"
      >
        <ShotButton />
        <TakeCards :shotgun="true" />
      </div>

      <!-- Простой сценарий -->
      <NextTurn v-else-if="isYouTurn && context.game?.take_flag" :context="context" />
      <TakeCards v-else :shotgun="false" />
      <BluffButton v-if="isCanBluffing" />
    </div>
  </section>
</template>
