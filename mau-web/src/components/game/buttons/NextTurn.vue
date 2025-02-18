<script setup lang="ts">
import { nextTurn } from '@/share/api'
import { ChevronRightCircle } from 'lucide-vue-next'
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-teal-500 flex gap-2"
    @click="nextTurn"
  >
    <ChevronRightCircle :size="24" />
    <div>Следующий ход</div>
  </button>
</template>
