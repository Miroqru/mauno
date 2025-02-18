<script setup lang="ts">
import type { GameContext } from '@/share/api/types'
import UnoCard from './UnoCard.vue'

const { context } = defineProps<{ context: GameContext }>()
</script>

<template>
  <section v-if="context.game" class="flex justify-around bg-stone-800 p-2 m-4 rounded-xl h-[40vh]">
    <UnoCard :card="context.game.deck.top" :active="true" class="align-middle my-auto" />
  </section>

  <!-- очень полезная информация -->
  <div class="flex-col gap-2 flex-wrap p-2 rounded-xl border-2 border-stone-700 m-2">
    <div class="flex gap-2">
      <div class="text-stone-400">
        Карт:
      </div>
      <div class="text-teal-300">
        {{ context.game?.deck.cards }}
      </div>
    </div>
    <div class="flex gap-2">
      <div class="text-stone-400">
        Использовано::
      </div>
      <div class="text-amber-300">
        {{ context.game?.deck.used }}
      </div>
    </div>

    <div class="flex gap-2">
      <div class="text-stone-400">
        Разворот:
      </div>
      <div class="text-orange-300">
        {{ context.game?.reverse }}
      </div>
    </div>
    <div class="flex gap-2">
      <div class="text-stone-400">
        Брали карту:
      </div>
      <div class="text-orange-300">
        {{ context.game?.take_flag }}
      </div>
    </div>
    <div class="flex gap-2">
      <div class="text-stone-400">
        Счётчик взятия:
      </div>
      <div class="text-purple-300">
        {{ context.game?.take_counter }}
      </div>
    </div>
    <div class="flex gap-2">
      <div class="text-stone-400">
        Револьвер:
      </div>
      <div class="text-pink-300">
        {{ context.game?.shotgun_current }}
      </div>
    </div>
    <div class="flex gap-2">
      <div class="text-stone-400">
        Начало игры:
      </div>
      <div class="text-emerald-300">
        {{ context.game?.game_started }}
      </div>
    </div>
    <div class="flex gap-2">
      <div class="text-stone-400">
        Начало хода:
      </div>
      <div class="text-green-300">
        {{ context.game?.turn_started }}
      </div>
    </div>
  </div>
</template>
