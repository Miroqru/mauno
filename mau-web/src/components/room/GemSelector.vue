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
      @click="emit('update', value - 5)"
      class="p-1 bg-stone-700 rounded-lg transition hover:bg-stone-600"
    >
      <Minus />
    </button>
    <div class="p-1 px-2 bg-stone-800 rounded-lg" v-else>
      <Minus />
    </div>

    <div class="p-1 px-2 rounded-md bg-stone-700">{{ value }}</div>

    <!-- plus -->
    <button
      v-if="value < 500"
      @click="emit('update', value + 5)"
      class="p-1 bg-stone-700 rounded-lg transition hover:bg-stone-600"
    >
      <Plus />
    </button>
    <div class="p-1 px-2 bg-stone-800 rounded-lg" v-else>
      <Plus />
    </div>
  </div>
</template>
