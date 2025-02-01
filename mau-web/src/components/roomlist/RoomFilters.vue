<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'
import { ArrowDownNarrowWide, ArrowDownWideNarrow } from 'lucide-vue-next'
import FilterButton from './FilterButton.vue'

const settingState = useSettingsStore()
</script>

<template>
  <div class="flex border-2 rounded-md border-stone-700 p-2 mb-4 gap-4">
    <button
      class="hover:color-teal-300"
      @click="settingState.roomFilter.invert = !settingState.roomFilter.invert"
    >
      <ArrowDownWideNarrow v-if="settingState.roomFilter.invert" />
      <ArrowDownNarrowWide v-else />
    </button>

    <div class="flex gap-2">
      <FilterButton name="Кристаллы" sort-by="gems" />
      <FilterButton name="участники" sort-by="players" />
    </div>
  </div>
</template>
