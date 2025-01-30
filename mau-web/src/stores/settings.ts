import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useSettingsState = defineStore('settings', () => {
  const topFilter = ref('crystals')

  return { topFilter }
})
