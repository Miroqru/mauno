<script setup lang="ts">
import PlayerCard from './PlayerCard.vue';

  const players = [
    {name: 'Qq Uwu', gems: 3578},
    {name: 'Miroq', gems: 1724},
    {name: 'Milinuri', gems: 100}
  ]

</script>

<template>
  <section class="my-4">
    <h2 class="text-xl font-bold">Игроки</h2>
    <PlayerCard v-for="[index, player] in players.entries()" :key="index" :name="player.name" :gems="player.gems" />
  </section>
</template>
