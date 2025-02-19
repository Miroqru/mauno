<script setup lang="ts">
import { Gem, Sparkle, User2 } from 'lucide-vue-next'
</script>

<template>
  <RouterLink
    to="/me"
    class="p-2 flex justify-between gap-2 my-4 bg-linear-160 from-pink-400/50 rounded-xl transition border-2 border-stone-800 hover:border-stone-600"
  >
    <div class="text-middle my-auto">
      <h2 class="color-stone-800 font-bold text-lg">Загрузка ...</h2>
      <div class="flex gap-2">
        <div class="flex text-stone-400 gap-1">? <Gem /></div>
        <div class="flex text-stone-400 gap-1">? место <Sparkle /></div>
      </div>
    </div>
    <User2 class="w-[64px] h-[64px] rounded-full" />
  </RouterLink>
</template>
