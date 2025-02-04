<script setup lang="ts">
import { getPlayersForRooms, getRooms } from '@/api'
import { useSettingsStore } from '@/stores/settings'
import type { Room, User } from '@/types'
import { computed, ref, watchEffect, type Ref } from 'vue'
import RoomCard from './RoomCard.vue'
import RoomFilters from './RoomFilters.vue'

const settingState = useSettingsStore()
const rooms = ref(getRooms())

const sortedRooms = computed(() => {
  let res: Room[] = []
  if (settingState.roomFilter.sortBy == 'gems') {
    // eslint-disable-next-line
    res = rooms.value.sort((a, b) => b.gems - a.gems)
  } else if (settingState.roomFilter.sortBy == 'players') {
    // eslint-disable-next-line
    res = rooms.value.sort((a, b) => b.players.length - a.players.length)
  }

  return settingState.roomFilter.invert ? res.slice().reverse() : res
})

const roomAndOwners: Ref<[Room, User][]> = ref([])
watchEffect(async () => (roomAndOwners.value = await getPlayersForRooms(sortedRooms.value)))
</script>

<template>
  <section class="my-4">
    <RoomFilters />
    <RoomCard v-for="[room, owner] in roomAndOwners" :key="room.id" :room="room" :owner="owner" />
  </section>
</template>
