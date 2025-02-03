<script setup lang="ts">
import { getRooms, getUserById } from '@/api'
import type { Room } from '@/types'
import { ref } from 'vue'
import RoomCard from '../roomlist/RoomCard.vue'
import CardHeader from './CardHeader.vue'

const rooms = ref(getRooms())

async function* roomIter(rooms: Room[]) {
  for (const room of rooms) {
    const owner = await getUserById(room.owner)
    if (!owner) {
      continue
    }
    yield { room, owner }
  }
}
</script>

<template>
  <section class="p-2 my-2">
    <CardHeader name="Открытые комнаты" to="/rooms" />
    <RoomCard
      v-for="{ room, owner } in roomIter(rooms)"
      :key="room.id"
      :owner="owner"
      :room="room"
    />
  </section>
</template>
