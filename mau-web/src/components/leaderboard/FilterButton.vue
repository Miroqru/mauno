<script setup lang="ts">
import type { Category } from '@/share/api/types'
import { useSettingsStore } from '@/share/stores/settings'

const props = defineProps<{
  name: string
  category: Category
}>()

const settingsState = useSettingsStore()
</script>

<template>
  <div
    v-if="settingsState.topFilter === props.category"
    class="p-2 bg-stone-700 rounded-lg transition hover:bg-stone-800"
  >
    {{ props.name }}
  </div>
  <button v-else class="text-stone-300" @click="settingsState.topFilter = props.category">
    {{ props.name }}
  </button>
</template>
