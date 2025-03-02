<script setup lang="ts">
import { Sparkle } from 'lucide-vue-next'

const { name, desc } = defineProps<{
  name: string
  desc: string
}>()
</script>

<template>
  <div class="my-2 p-2 bg-stone-800 rounded-md flex gap-4 text-center">
    <Sparkle :size="48" />
    <div class="flex-1">
      <div class="font-bold text-md">{{ name }}.</div>
      <div>{{ desc }}</div>
    </div>
  </div>
</template>
