<script setup lang="ts">
import { newRoom } from '@/share/api'
import { Plus } from 'lucide-vue-next'

const { showName } = defineProps<{ showName?: boolean }>()
</script>

<template>
  <button
    class="bg-stone-700 p-4 md:p-3 rounded-full flex gap-2 transition hover:bg-stone-600"
    @click="newRoom"
  >
    <Plus :size="24" />
    <div v-if="showName">Комнату</div>
  </button>
</template>
[]
