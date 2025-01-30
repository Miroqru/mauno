<script setup lang="ts">
import GameSettings from './buttons/GameSettings.vue'
import NextTurn from './buttons/NextTurn.vue'
import TakeCards from './buttons/TakeCards.vue'
</script>

<template>
  <section class="flex justify-between my-4">
    <GameSettings />
    <TakeCards />
    <NextTurn />
  </section>
</template>
