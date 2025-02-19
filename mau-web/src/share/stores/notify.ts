import type { Ref } from 'vue'
import dayjs from 'dayjs'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type NotifyType = 'info' | 'success' | 'warning' | 'error'

export interface Notify {
  id: string
  name: string
  body: any
  type: NotifyType
}

export const useNotifyStore = defineStore('notify', () => {
  const notifies: Ref<Notify[]> = ref([])

  function removeNotify(id: string) {
    notifies.value = notifies.value.filter((notify) => notify.id !== id)
  }

  function addNotify(name: string, body: any, type: NotifyType) {
    const id = dayjs().format()
    const notify: Notify = { id, name, body, type }

    notifies.value.push(notify)
    setTimeout(() => removeNotify(notify.id), 3600)
  }

  return { notifies, addNotify, removeNotify }
})
