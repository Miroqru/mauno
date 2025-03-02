<script setup lang="ts">
import { leaveGame } from '@/share/api'
import { DoorOpen } from 'lucide-vue-next'
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-pink-500 flex gap-2"
    @click="() => leaveGame"
  >
    <DoorOpen :size="24" />
    <div>Выйти</div>
  </button>
</template>
