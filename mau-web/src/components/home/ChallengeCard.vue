<script setup lang="ts">
import type { Challenge } from '@/share/api/types'
import { Gem } from 'lucide-vue-next'

const { challenge } = defineProps<{ challenge: Challenge }>()
</script>

<template>
  <div class="flex gap-2 md:gap-4 justify-around m-2 bg-stone-900 p-1 rounded-md">
    <div class="text-middle m-auto flex-1 font-bold">
      {{ challenge.name }}
    </div>
    <div class="h-[24px] m-auto text-stone-300">
      {{ challenge.now }} / {{ challenge.total }}
    </div>
    <div class="inline-flex gap-1 text-middle m-auto text-pink-300">
      {{ challenge.reward }} <Gem :size="24" />
    </div>
  </div>
</template>
