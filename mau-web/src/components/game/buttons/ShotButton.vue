<script setup lang="ts">
import { shotgunShot } from '@/share/api'
import { Flame } from 'lucide-vue-next'
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-pink-500 flex gap-2"
    @click="shotgunShot"
  >
    <Flame :size="24" />
    <div>Следующий ход</div>
  </button>
</template>
