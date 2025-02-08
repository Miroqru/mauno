<script setup lang="ts">
import type { Room } from '@/types'
import type { Ref } from 'vue'
import { getRooms } from '@/api'
import { useSettingsStore } from '@/stores/settings'
import { Squirrel } from 'lucide-vue-next'
import { ref, watchEffect } from 'vue'
import NewGame from '../buttons/NewGame.vue'
import RoomCard from './RoomCard.vue'
import RoomFilters from './RoomFilters.vue'

const settingState = useSettingsStore()
const rooms: Ref<Room[]> = ref([])

watchEffect(async () => {
  const res = await getRooms(settingState.roomFilter)
  if (!res.error) {
    rooms.value = res.data
  }
})
</script>

<template>
  <section class="my-4">
    <RoomFilters />
    <div v-if="rooms.length">
      <RoomCard v-for="room in rooms" :key="room.id" :room="room" />
    </div>
    <div v-else class="justify-center flex flex-col text-center">
      <Squirrel :size="128" class="align-center mx-auto mb-2 text-stone-200" />
      <div>
        <div class="font-bold text-stone-200 text-lg">
          Сейчас никто не играет
        </div>
        <div class="text-stone-300">
          как насчёт того, чтобы создать новую комнату!
        </div>
        <NewGame :show-name="true" class="align-center mx-auto" />
      </div>
    </div>
  </section>
</template>
