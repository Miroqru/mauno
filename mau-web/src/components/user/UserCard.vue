<script setup lang="ts">
import { Gem } from 'lucide-vue-next'
</script>

<template>
  <RouterLink
    to="/me"
    class="p-2 flex justify-between gap-2 my-4 bg-linear-160 from-pink-300/30 rounded-xl"
  >
    <div class="text-middle my-auto">
      <h2 class="color-stone-800 font-bold text-lg">Milinuri</h2>
      <div class="flex text-stone-400 gap-1"><Gem :size="18" /> 100</div>
    </div>
    <img src="https://placewaifu.com/image/200" class="w-[64px] h-[64px] rounded-full" />
  </RouterLink>
</template>
