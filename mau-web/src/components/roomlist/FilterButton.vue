<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'

const { name, sortBy } = defineProps<{ name: string; sortBy: string }>()
const settingState = useSettingsStore()
</script>

<template>
  <div class="bg-teal-800 p-1 rounded-md" v-if="sortBy == settingState.roomFilter.sortBy">
    {{ name }}
  </div>
  <button
    v-else
    class="bg-stone-800 p-1 rounded-md transition hover:bg-stone-700"
    @click="settingState.roomFilter.sortBy = sortBy"
  >
    {{ name }}
  </button>
</template>
