<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'
import type { RoomOrder } from '@/types'
import { ArrowDownNarrowWide, ArrowDownWideNarrow } from 'lucide-vue-next'
import FilterButton from './FilterButton.vue'

const settingState = useSettingsStore()

const filters: { name: string; orderBy: RoomOrder }[] = [
  { name: 'Дата', orderBy: 'create_time' },
  { name: 'Кристаллы', orderBy: 'gems' },
  { name: 'Игроки', orderBy: 'players' },
]
</script>

<template>
  <div class="flex border-2 rounded-md border-stone-700 p-2 mb-4 gap-4">
    <button
      class="hover:color-teal-300"
      @click="settingState.roomFilter.reverse = !settingState.roomFilter.reverse"
    >
      <ArrowDownWideNarrow v-if="settingState.roomFilter.reverse" />
      <ArrowDownNarrowWide v-else />
    </button>

    <div class="flex gap-2">
      <FilterButton
        v-for="filter in filters"
        :key="filter.orderBy"
        :name="filter.name"
        :order-by="filter.orderBy"
      />
    </div>
  </div>
</template>
