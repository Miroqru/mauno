<script setup lang="ts">
import { skipPlayer } from '@/share/api'
import { StepForward } from 'lucide-vue-next'
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-violet-700 flex gap-2"
    @click="skipPlayer"
  >
    <StepForward :size="24" />
  </button>
</template>
