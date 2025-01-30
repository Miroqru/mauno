<script setup lang="ts">
import UnoCard from './UnoCard.vue'
const hand = [
  { name: '+2', image: 'b_take', active: true },
  { name: '+2', image: 'g_take', active: true },
  { name: 'yellow 5', image: 'y_5', active: false },
  { name: 'green skip', image: 'g_skip', active: false },
  { name: 'res 3', image: 'r_3', active: false },
  { name: 'yellow 5', image: 'y_2', active: false },
]
</script>

<template>
  <section class="flex justify-center gap-2 flex-wrap overflow-x-auto h-[15vh]">
    <UnoCard
      v-for="[index, card] in hand.entries()"
      :key="index"
      :name="card.name"
      :active="card.active"
      :image="card.image"
    />
  </section>
</template>
