<script setup lang="ts">
import type { Category } from '@/api'
import FilterButton from './FilterButton.vue'

const categoryButtons: { name: string; category: Category }[] = [
  { name: 'Игр', category: 'games' },
  { name: 'Побед', category: 'wins' },
  { name: 'карт', category: 'cards' },
  { name: 'Кристаллов', category: 'gems' },
]
</script>

<template>
  <section class="flex border-2 border-stone-600 rounded-md justify-around mb-4">
    <FilterButton
      v-for="item in categoryButtons"
      :key="item.name"
      :name="item.name"
      :category="item.category"
    />
  </section>
</template>
