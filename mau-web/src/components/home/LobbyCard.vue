<script setup lang="ts">
import { Gem } from 'lucide-vue-next'
</script>

<template>
  <div class="flex justify-around m-2 bg-stone-900 p-1 rounded-md">
    <div class="inline-flex gap-2 flex-1">
      <img src="https://placewaifu.com/image/200" class="w-[32px] h-[32px] rounded-full" />
      <div class="text-middle m-auto flex-1 font-bold">Qq UwU</div>
    </div>
    <div class="mr-4 h-[24px] m-auto text-stone-300">1/5</div>
    <div class="inline-flex gap-1 mr-2 text-middle m-auto text-teal-200">30 <Gem :size="24" /></div>
  </div>
</template>
