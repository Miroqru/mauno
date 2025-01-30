<script setup lang="ts">
import PlayerAvatar from './PlayerAvatar.vue'
const players = [
  {
    name: 'Qq Uwu',
    avatarUrl: 'https://placewaifu.com/image/200',
    active: false,
    cards: 3,
  },
  {
    name: 'Miroq',
    avatarUrl: 'https://placewaifu.com/image/200',
    active: false,
    cards: 1,
  },
  {
    name: 'Qq Uwu',
    avatarUrl: 'https://placewaifu.com/image/200',
    active: true,
    cards: 5,
  },

]
</script>

<template>
  <section class="flex justify-around my-4">
    <PlayerAvatar
      v-for="player in players"
      :key="player.name"
      :name="player.name"
      :avatar-url="player.avatarUrl"
      :active="player.active"
      :cards="player.cards"
    />
  </section>
</template>
