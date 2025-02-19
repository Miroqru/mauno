import type { Category, RoomFilter, RoomOrder } from '@/share/api/types'
import { defineStore } from 'pinia'
import type { Ref } from 'vue'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const topFilter: Ref<Category> = ref('gems')
  const roomFilter: Ref<RoomFilter> = ref({
    reverse: false,
    orderBy: 'create_time' as RoomOrder,
  })

  return { topFilter, roomFilter }
})
