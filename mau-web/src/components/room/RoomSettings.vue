<script setup lang="ts">
import type { Room, RoomDataIn } from '@/types'

import type { Ref } from 'vue'
import { updateRoom } from '@/api'
import { useUserStore } from '@/stores/user'
import { Check, CheckCircle, Circle } from 'lucide-vue-next'
import { ref } from 'vue'
import GemSelector from './GemSelector.vue'
import RangeSelector from './RangeSelector.vue'

const { room } = defineProps<{ room: Room }>()

const userState = useUserStore()
const settings: Ref<RoomDataIn> = ref({
  name: room.name,
  private: room.private,
  room_password: room.room_password,
  gems: room.gems,
  min_players: room.min_players,
  max_players: room.max_players,
})
const errorBadge = ref(null)

async function updateRoomSubmit() {
  const res = await updateRoom(room.id, userState.userToken as string, settings.value)
  if (res.type === 'left') {
    errorBadge.value = res.value
  }
}
</script>

<template>
  <section class="my-4 md:border-2 md:border-stone-700 rounded-md md:p-2">
    <h2 class="text-xl font-bold mb-2 text-center">
      Настройки комнаты
    </h2>

    <div v-if="errorBadge" class="bg-pink-800 p-2 border-2 border-pink-600 rounded-md mv-2">
      {{ errorBadge }}
    </div>

    <div class="flex flex-col gap-2 mb-2">
      <input
        v-model="settings.name"
        type="text"
        class="focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 mx-2 bg-stone-800 border-2 border-stone-700 transition rounded-xl"
        placeholder="Имя комнаты"
      >

      <input
        v-model="settings.room_password"
        type="password"
        class="focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 mx-2 bg-stone-800 border-2 border-stone-700 transition rounded-xl"
        placeholder="Пароль для входа"
      >
    </div>

    <div class="flex gap-2 mb-2">
      <button @click="settings.private = !settings.private">
        <CheckCircle v-if="settings.private" class="text-teal-200" />
        <Circle v-else />
      </button>
      <div>Приватная комната</div>
    </div>

    <div class="mb-2 justify-between flex gap-4">
      <div>Максимум игроков</div>
      <RangeSelector
        :value="settings.max_players"
        @update="(newValue) => (settings.max_players = newValue)"
      />
    </div>

    <div class="mb-2 justify-between flex gap-4">
      <div>Минимум игроков</div>
      <RangeSelector
        :value="settings.min_players"
        @update="(newValue) => (settings.min_players = newValue)"
      />
    </div>

    <div class="mb-4 justify-between flex gap-4">
      <div>Ставка</div>
      <GemSelector :value="settings.gems" @update="(newValue) => (settings.gems = newValue)" />
    </div>

    <div class="flex flex-row-reverse gap-2">
      <button
        class="p-1 bg-stone-700 rounded-lg transition hover:bg-teal-600 flex gao-4"
        @click="updateRoomSubmit"
      >
        <Check /> Применить
      </button>
    </div>
  </section>
</template>
