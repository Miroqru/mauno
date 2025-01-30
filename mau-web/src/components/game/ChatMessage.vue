<script setup lang="ts">
  const props = defineProps<{
    name: string
    message: string
  }>()
</script>

<template>
  <div class="flex gap-2 my-2">
    <div class="text-teal-200 font-bold">{{ props.name }}</div>
    <div>{{ props.message }}</div>
  </div>
</template>
