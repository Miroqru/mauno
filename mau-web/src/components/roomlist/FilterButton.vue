<script setup lang="ts">
import type { RoomOrder } from '@/share/api/types'
import { useSettingsStore } from '@/share/stores/settings'

const { name, orderBy } = defineProps<{ name: string, orderBy: RoomOrder }>()
const settingState = useSettingsStore()
</script>

<template>
  <div v-if="orderBy === settingState.roomFilter.orderBy" class="bg-teal-800 px-2 rounded-md">
    {{ name }}
  </div>
  <button
    v-else
    class="bg-stone-800 px-2 rounded-md transition hover:bg-stone-700"
    @click="settingState.roomFilter.orderBy = orderBy"
  >
    {{ name }}
  </button>
</template>
