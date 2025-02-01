<script setup lang="ts">
import { getRooms } from '@/api'
import { useSettingsStore } from '@/stores/settings'
import type { Room } from '@/types'
import { computed, ref } from 'vue'
import RoomCard from './RoomCard.vue'
import RoomFilters from './RoomFilters.vue'

const settingState = useSettingsStore()
const rooms = ref(getRooms())

const sortedRooms = computed(() => {
  let res: Room[] = []
  if (settingState.roomFilter.sortBy == 'gems') {
    res = rooms.value.sort((a, b) => b.gems - a.gems)
  } else if (settingState.roomFilter.sortBy == 'players') {
    res = rooms.value.sort((a, b) => b.players.length - a.players.length)
  }

  return settingState.roomFilter.invert ? res.slice().reverse() : res
})
</script>

<template>
  <section class="my-4">
    <RoomFilters />
    <RoomCard v-for="room in sortedRooms" :key="room.id" :room="room" />
  </section>
</template>
