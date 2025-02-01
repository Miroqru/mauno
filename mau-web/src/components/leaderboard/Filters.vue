<script setup lang="ts">
import FilterButton from './FilterButton.vue'
</script>

<template>
  <section class="flex border-2 border-stone-600 rounded-md justify-around mb-4">
    <FilterButton name="игр" filter="games" />
    <FilterButton name="побед" filter="wins" />
    <FilterButton name="Карт" filter="cards" />
    <FilterButton name="Кристаллов" filter="gems" />
  </section>
</template>
