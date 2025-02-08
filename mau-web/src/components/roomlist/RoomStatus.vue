<script setup lang="ts">
import type { RoomStatus } from '@/types'

const { status } = defineProps<{ status: RoomStatus }>()
</script>

<template>
  <div
    class="rounded-full bg-teal-400 text-teal-900 font-bold m-2 px-2 align-middle my-auto text-sm"
    v-if="status == 'idle'"
  >
    Отдых
  </div>
  <div
    class="rounded-full bg-sky-400 text-sky-900 font-bold m-2 px-2 align-middle my-auto text-sm"
    v-else-if="status == 'game'"
  >
    Игра
  </div>
  <div
    class="rounded-full bg-pink-400 text-pink-900 font-bold m-2 px-2 align-middle my-auto text-sm"
    v-else-if="status == 'ended'"
  >
    Завершена
  </div>
  <div
    class="rounded-full bg-stone-500 text-stone-900 font-bold m-2 px-2 align-middle my-auto text-sm"
    v-else
  >
    {{ status }}
  </div>
</template>
