<script setup lang="ts">
import { useNotifyStore } from '@/share/stores/notify'
import { Settings } from 'lucide-vue-next'

const notifyState = useNotifyStore()
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-stone-500"
    @click="notifyState.addNotify('А где...?', 'Настройки будут позже', 'warning')"
  >
    <Settings :size="24" />
  </button>
</template>
