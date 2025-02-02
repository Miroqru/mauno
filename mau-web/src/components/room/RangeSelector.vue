<script setup lang="ts">
const { value } = defineProps<{ value: number }>()
const emit = defineEmits<{ update: [number] }>()
</script>

<template>
  <div class="flex gap-2">
    <div v-for="x in [2, 3, 4, 5, 6, 7]" :key="x">
      <button
        class="p-1 px-2 bg-stone-700 rounded-lg transition hover:bg-stone-600"
        v-if="x != value"
        @click="emit('update', x)"
      >
        {{ x }}
      </button>
      <div class="p-1 px-2 bg-teal-600 rounded-lg" v-else>{{ x }}</div>
    </div>
  </div>
</template>
