<script setup lang="ts">
const { value } = defineProps<{ value: number }>()
const emit = defineEmits<{ update: [number] }>()
</script>

<template>
  <div class="flex gap-2">
    <div v-for="x in [2, 3, 4, 5, 6, 7]" :key="x">
      <button
        v-if="x !== value"
        class="p-1 px-2 bg-stone-700 rounded-lg transition hover:bg-stone-600"
        @click="emit('update', x)"
      >
        {{ x }}
      </button>
      <div v-else class="p-1 px-2 bg-teal-600 rounded-lg">
        {{ x }}
      </div>
    </div>
  </div>
</template>
