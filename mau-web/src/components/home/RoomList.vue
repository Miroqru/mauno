<script setup lang="ts">
import { getPlayersForRooms, getRooms } from '@/api'
import type { Room, User } from '@/types'
import { onMounted, ref, type Ref } from 'vue'
import RoomCard from '../roomlist/RoomCard.vue'
import CardHeader from './CardHeader.vue'

const rooms = ref(getRooms())
const roomAndOwners: Ref<[Room, User][]> = ref([])

onMounted(async () => {
  roomAndOwners.value = await getPlayersForRooms(rooms.value)
})
</script>

<template>
  <section class="p-2 my-2">
    <CardHeader name="Открытые комнаты" to="/rooms" />
    <RoomCard v-for="[room, owner] in roomAndOwners" :key="room.id" :owner="owner" :room="room" />
  </section>
</template>
