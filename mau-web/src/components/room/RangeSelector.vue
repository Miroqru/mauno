<script setup lang="ts">
const props = defineProps<{
  value: number
}>()
</script>

<template>
  <div class="flex gap-2">
    <div v-for="x in [2, 3, 4, 5, 6, 7]" :key="x">
      <button class="p-1 px-2 bg-stone-800 rounded-lg" v-if="x != value">{{ x }}</button>
      <div class="p-1 px-2 bg-teal-600 rounded-lg" v-else>{{ x }}</div>
    </div>
  </div>
</template>
