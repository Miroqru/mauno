import type { Category } from '@/api'
import type { RoomFilter, RoomOrder } from '@/types'
import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const topFilter: Ref<Category> = ref('gems')
  const roomFilter: Ref<RoomFilter> = ref({
    reverse: false,
    orderBy: 'create_time' as RoomOrder,
  })

  return { topFilter, roomFilter }
})
