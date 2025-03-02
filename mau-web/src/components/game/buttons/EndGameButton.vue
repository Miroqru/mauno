<script setup lang="ts">
import { endGame } from '@/share/api'
import { CircleX } from 'lucide-vue-next'
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-amber-500 flex gap-2"
    @click="endGame"
  >
    <CircleX :size="24" />
    <div>Завершить</div>
  </button>
</template>
