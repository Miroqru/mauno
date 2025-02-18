<script setup lang="ts">
import type { Player } from '@/share/api/types'
import UnoCard from './UnoCard.vue'

const { player } = defineProps<{ player: Player }>()
</script>

<template>
  <section class="flex justify-center gap-2 flex-wrap overflow-x-auto h-[15vh] md:h-[30vh]">
    <UnoCard
      v-for="[index, card] in player.hand.cover.entries()"
      :key="index"
      :card="card"
      :active="true"
    />
    <UnoCard
      v-for="[index, card] in player.hand.uncover.entries()"
      :key="index"
      :card="card"
      :active="false"
    />
  </section>
</template>
