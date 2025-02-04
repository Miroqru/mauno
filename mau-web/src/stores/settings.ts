import type { Category } from '@/api'
import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const topFilter: Ref<Category> = ref('gems')
  const roomFilter = ref({
    invert: false,
    sortBy: 'gems',
  })

  return { topFilter, roomFilter }
})
