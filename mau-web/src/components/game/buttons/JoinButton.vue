<script setup lang="ts">
import { joinGame } from '@/share/api/api'
import { Play } from 'lucide-vue-next'
// hello
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-teal-500 flex gap-2"
    @click="joinGame"
  >
    <Play :size="24" />
    <div>Зайти</div>
  </button>
</template>
