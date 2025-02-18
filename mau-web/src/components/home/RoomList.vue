<script setup lang="ts">
import { getRooms } from '@/share/api'
import type { Room } from '@/share/api/types'
import { Squirrel } from 'lucide-vue-next'
import type { Ref } from 'vue'
import { onMounted, ref } from 'vue'
import NewGame from '../buttons/NewGame.vue'
import RoomCard from '../roomlist/RoomCard.vue'
import CardHeader from './CardHeader.vue'

const rooms: Ref<Room[]> = ref([])

onMounted(async () => {
  rooms.value = await getRooms()
})
</script>

<template>
  <section class="p-2 my-2 md:rounded-md md:border-3 md:border-stone-700">
    <CardHeader name="Открытые комнаты" to="/rooms" />
    <div v-if="rooms.length">
      <RoomCard v-for="room in rooms" :key="room.id" :room="room" />
    </div>
    <div v-else class="justify-center flex flex-col text-center">
      <Squirrel :size="128" class="align-center mx-auto mb-2 text-stone-200" />
      <div>
        <div class="font-bold text-stone-200 text-lg">Сейчас никто не играет</div>
        <div class="text-stone-300">как насчёт того, чтобы создать новую комнату!</div>
        <NewGame :show-name="true" class="align-center mx-auto" />
      </div>
    </div>
  </section>
</template>
