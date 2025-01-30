<script setup lang="ts">
import { Gem, User } from 'lucide-vue-next'
</script>

<template>
  <section
    class="flex text-center justify-between bg-linear-160 from-teal-300/40 rounded-xl p-2 mb-4"
  >
    <div class="text-middle m-auto">
      <div class="font-bold text-xl m-2">Комната Milinuri</div>
      <div class="flex text-center gap-4 justify-center text-stone-400">
        <div class="flex gap-1">100 <Gem /></div>
        <div class="flex gap-1">1 / 3 <User /></div>
      </div>
    </div>
    <img src="https://placewaifu.com/image/200" class="w-[128px] h-[128px] rounded-full p-2" />
  </section>
</template>
