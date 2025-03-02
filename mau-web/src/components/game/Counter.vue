<script setup lang="ts">
const { value } = defineProps<{ value: number }>()
</script>

<template>
  <div
    class="absolute -bottom-1 -right-1 bg-stone-600 px-2 font-bold rounded-full"
    :class="{ 'border-amber-500 border-2 text-amber-100': value === 1 }"
  >
    {{ value }}
  </div>
</template>
