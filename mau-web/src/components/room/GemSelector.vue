<script setup lang="ts">
import { Minus, Plus } from 'lucide-vue-next'

const { value } = defineProps<{ value: number }>()
const emit = defineEmits<{ update: [number] }>()
</script>

<template>
  <div class="flex gap-2">
    <!-- minus -->
    <button
      v-if="value >= 10"
      class="p-1 bg-stone-700 rounded-lg transition hover:bg-stone-600"
      @click="emit('update', value - 5)"
    >
      <Minus />
    </button>
    <div v-else class="p-1 px-2 bg-stone-800 rounded-lg">
      <Minus />
    </div>

    <div class="p-1 px-2 rounded-md bg-stone-700">
      {{ value }}
    </div>

    <!-- plus -->
    <button
      v-if="value < 500"
      class="p-1 bg-stone-700 rounded-lg transition hover:bg-stone-600"
      @click="emit('update', value + 5)"
    >
      <Plus />
    </button>
    <div v-else class="p-1 px-2 bg-stone-800 rounded-lg">
      <Plus />
    </div>
  </div>
</template>
