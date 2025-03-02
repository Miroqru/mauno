<script setup lang="ts">
import { randomRoom } from '@/share/api'
import { Shuffle } from 'lucide-vue-next'

const { showName } = defineProps<{ showName?: boolean }>()
</script>

<template>
  <button
    class="bg-stone-700 p-4 md:p-3 rounded-full flex gap-2 transition hover:bg-stone-600"
    @click="randomRoom"
  >
    <Shuffle :size="24" />
    <div v-if="showName">Случайная</div>
  </button>
</template>
