<script setup lang="ts">
import RoomCard from './RoomCard.vue'

const rooms = [
  {
    name: 'Qq Uwu',
    avatarUrl: 'https://placewaifu.com/image/200',
    players: 1,
    maxPlayers: 2,
    crystals: 75,
  },
  {
    name: 'Miroq',
    avatarUrl: 'https://placewaifu.com/image/200',
    players: 2,
    maxPlayers: 5,
    crystals: 20,
  },
  {
    name: 'Rumia',
    avatarUrl: 'https://placewaifu.com/image/200',
    players: 1,
    maxPlayers: 3,
    crystals: 250,
  },
]
</script>

<template>
  <section class="my-4">
    <RoomCard
      v-for="[index, room] in rooms.entries()"
      :key="index"
      :name="room.name"
      :avatar-url="room.avatarUrl"
      :players="room.players"
      :max-players="room.maxPlayers"
      :crystals="room.crystals"
    />
  </section>
</template>
