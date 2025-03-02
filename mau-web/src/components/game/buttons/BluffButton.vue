<script setup lang="ts">
import { bluffCard } from '@/share/api'
import { MessageCircleWarning } from 'lucide-vue-next'
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-pink-500 flex gap-2"
    @click="bluffCard"
  >
    <MessageCircleWarning :size="24" />
    <div>Не верю!</div>
  </button>
</template>
