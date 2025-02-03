<script setup lang="ts">
import { Check, CheckCircle, Circle } from 'lucide-vue-next'

import { useUserStore } from '@/stores/user'
import type { Room } from '@/types'
import { ref } from 'vue'
import GemSelector from './GemSelector.vue'
import RangeSelector from './RangeSelector.vue'

const userstate = useUserStore()
const { room } = defineProps<{ room: Room }>()

const isPrivate = ref(room.private)
const maxPlayers = ref(room.maxPlayers)
const minPlayers = ref(room.minPlayers)
const gems = ref(room.gems)
</script>

<template>
  <section class="my-4 md:border-2 md:border-stone-700 rounded-md md:p-2">
    <h2 class="text-xl font-bold mb-2">Настройки комнаты</h2>

    <div class="flex gap-2 mb-2">
      <button @click="isPrivate = !isPrivate">
        <CheckCircle v-if="isPrivate" class="text-teal-200" />
        <Circle v-else />
      </button>
      <div>Приватная комната</div>
    </div>

    <div class="mb-2 justify-between flex gap-4">
      <div>Максимум игроков</div>
      <RangeSelector :value="maxPlayers" @update="(newValue) => (maxPlayers = newValue)" />
    </div>

    <div class="mb-2 justify-between flex gap-4">
      <div>Минимум игроков</div>
      <RangeSelector :value="minPlayers" @update="(newValue) => (minPlayers = newValue)" />
    </div>

    <div class="mb-2 justify-between flex gap-4">
      <div>Ставка</div>
      <GemSelector :value="gems" @update="(newValue) => (gems = newValue)" />
    </div>

    <button class="p-1 bg-stone-700 rounded-lg transition hover:bg-teal-600 flex gao-4">
      <Check /> Применить
    </button>
  </section>
</template>
