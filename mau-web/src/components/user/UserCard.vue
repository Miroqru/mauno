<script setup lang="ts">
  import { Gem } from 'lucide-vue-next'
</script>

<template>
  <section class="p-2 flex justify-between gap-2 my-4">
    <div>
      <h2 class="color-stone-800 font-bold text-lg">Milinuri</h2>
      <div class="flex text-stone-400"><Gem :size="18"/> 100</div>
    </div>
    <RouterLink to="/me">
      <img src="https://placewaifu.com/image/200" class="w-[64px] h-[64px] rounded-full"/>
    </RouterLink>
  </section>
</template>
