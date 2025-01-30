<script setup lang="ts">
const props = defineProps<{
  index: number
  name: string
  value: number
}>()
</script>

<template>
  <div class="flex justify-between bg-stone-800 rounded-md mb-2">
    <div class="text-amber-50 mx-2 text-middle my-auto">{{ props.index }}</div>
    <div class="flex gap-2 flex-1">
      <img src="https://placewaifu.com/image/200" class="w-[32px] h-[32px] rounded-full" />
      <div class="flex-1 text-middle my-auto">{{ props.name }}</div>
    </div>
    <div class="text-amber-200 mx-2 text-middle my-auto">{{ props.value }}</div>
  </div>
</template>
