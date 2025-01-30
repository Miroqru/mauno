<script setup lang="ts">
import { Gem } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
</script>

<template>
  <section
    class="flex text-center justify-between bg-linear-160 from-pink-300/30 rounded-xl p-2 mb-4"
  >
    <img src="https://placewaifu.com/image/200" class="w-[128px] h-[128px] rounded-full p-2" />
    <div class="text-middle m-auto">
      <div class="font-bold text-xl m-2">Milinuri</div>
      <div class="flex text-center gap-4 justify-center text-stone-400">
        <div class="flex gap-1">100 <Gem /></div>
        <RouterLink to="/top">3 место</RouterLink>
      </div>
    </div>
  </section>
</template>
