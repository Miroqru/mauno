<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'

const props = defineProps<{
  name: string
  filter: string
}>()

const settingsState = useSettingsStore()
</script>

<template>
  <div
    v-if="settingsState.topFilter === props.filter"
    class="p-2 bg-stone-700 rounded-lg transition hover:bg-stone-800"
  >
    {{ props.name }}
  </div>
  <button v-else class="text-stone-300" @click="settingsState.topFilter = props.filter">
    {{ props.name }}
  </button>
</template>
