<script setup lang="ts">
import type { RoomStatus } from '@/share/api/types'

const { status } = defineProps<{ status: RoomStatus }>()
</script>

<template>
  <div
    v-if="status === 'idle'"
    class="rounded-full bg-teal-400 text-teal-900 font-bold m-2 px-2 align-middle my-auto text-sm"
  >
    Отдых
  </div>
  <div
    v-else-if="status === 'game'"
    class="rounded-full bg-sky-400 text-sky-900 font-bold m-2 px-2 align-middle my-auto text-sm"
  >
    Игра
  </div>
  <div
    v-else-if="status === 'ended'"
    class="rounded-full bg-pink-400 text-pink-900 font-bold m-2 px-2 align-middle my-auto text-sm"
  >
    Завершена
  </div>
  <div
    v-else
    class="rounded-full bg-stone-500 text-stone-900 font-bold m-2 px-2 align-middle my-auto text-sm"
  >
    {{ status }}
  </div>
</template>
