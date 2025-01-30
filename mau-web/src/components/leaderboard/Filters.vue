<script setup lang="ts">
import FilterButton from './FilterButton.vue'
</script>

<template>
  <section class="flex border-2 border-stone-600 rounded-md justify-around mb-4">
    <FilterButton name="игры" filter="games" />
    <FilterButton name="победы" filter="wins" />
    <FilterButton name="кристаллы" filter="crystals" />
  </section>
</template>
