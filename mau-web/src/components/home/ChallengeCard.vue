<script setup lang="ts">
import { Gem } from 'lucide-vue-next'

const props = defineProps<{
  desc: string
  now: number
  total: number
  reward: number
}>()
</script>

<template>
  <div class="flex justify-around m-2 bg-stone-900 p-1 rounded-md">
    <div class="text-middle m-auto flex-1 font-bold">{{ props.desc }}</div>
    <div class="mr-4 h-[24px] m-auto text-stone-300">{{ props.now }} / {{ props.total }}</div>
    <div class="inline-flex gap-1 mr-2 text-middle m-auto text-pink-300">
      {{ props.reward }} <Gem :size="24" />
    </div>
  </div>
</template>
