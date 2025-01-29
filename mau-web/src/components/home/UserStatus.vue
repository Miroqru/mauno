<script setup lang="ts">
  import { Gem } from 'lucide-vue-next'

  const props = defineProps<{
    name: string
    gems: number
  }>()
</script>

<template>
  <div class="flex justify-around m-2 bg-stone-900 p-1 rounded-md">
    <div class="inline-flex gap-2 flex-1">
      <img src="https://placewaifu.com/image/200" class="w-[32px] h-[32px] rounded-full"/>
      <div class="text-middle m-auto flex-1 font-bold text-amber-503">
        {{ props.name }}
      </div>
    </div>
    <div class="inline-flex gap-1 mr-2 text-middle m-auto text-amber-200">
      {{ props.gems }} <Gem :size="24" />
    </div>
  </div>
</template>
