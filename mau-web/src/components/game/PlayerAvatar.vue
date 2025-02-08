<script setup lang="ts">
const props = defineProps<{
  name: string
  avatarUrl: string
  active: boolean
  cards: number
}>()
</script>

<template>
  <div
    class="w-[64px] h-[64px] border-2 rounded-full border-stone-400 relative"
    :class="{ 'border-teal-300': props.active }"
  >
    <img :src="props.avatarUrl" :alt="props.name" class="rounded-full border-2 border-stone-800">
    <div
      class="absolute -bottom-1 -right-1 bg-stone-600 px-2 font-bold rounded-full"
      :class="{ 'border-amber-500 border-2 text-amber-100': props.cards === 1 }"
    >
      {{ props.cards }}
    </div>
  </div>
</template>
