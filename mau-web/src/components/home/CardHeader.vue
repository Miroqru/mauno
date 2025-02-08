<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'

const props = defineProps<{
  name: string
  to: string
}>()
</script>

<template>
  <RouterLink :to="props.to" class="group flex justify-between mb-2">
    <h2 class="text-lg font-bold">
      {{ props.name }}
    </h2>
    <ChevronRight class="text-stone-400 transition group-hover:text-teal-400" />
  </RouterLink>
</template>
