<script setup lang="ts">
import type { GameContext } from '@/share/api/types'
import PlayerAvatar from './PlayerAvatar.vue'

const { context } = defineProps<{ context: GameContext }>()
</script>

<template>
  <section v-if="context.game" class="flex flex-wrap justify-center gap-2 md:gap-4 my-4">
    <PlayerAvatar
      v-for="[index, player] in context.game.players.entries()"
      :key="index"
      :player="player"
      :active="index === context.game.current_player"
    />
  </section>
</template>
