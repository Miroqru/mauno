<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'
import type { RoomOrder } from '@/types'

const { name, orderBy } = defineProps<{ name: string; orderBy: RoomOrder }>()
const settingState = useSettingsStore()
</script>

<template>
  <div class="bg-teal-800 px-2 rounded-md" v-if="orderBy == settingState.roomFilter.orderBy">
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
