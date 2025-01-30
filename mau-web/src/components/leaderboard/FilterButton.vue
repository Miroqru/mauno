<script setup lang="ts">
import { useSettingsState } from '@/stores/settings'

const props = defineProps<{
  name: string
  filter: string
}>()

const settingsState = useSettingsState()
</script>

<template>
  <div v-if="settingsState.topFilter === props.filter" class="p-2 bg-stone-700 rounded-lg">
    {{ props.name }}
  </div>
  <button v-else class="text-stone-300" @click="settingsState.topFilter = props.filter">
    {{ props.name }}
  </button>
</template>
