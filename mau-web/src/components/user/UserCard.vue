<script setup lang="ts">
import type { User } from '@/types'
import { Gem, Sparkle } from 'lucide-vue-next'

const { user } = defineProps<{
  user: User
}>()

// TODO: Подгрузка информации о месте пользователя
</script>

<template>
  <RouterLink
    to="/me"
    class="p-2 flex justify-between gap-2 my-4 bg-linear-160 from-pink-400/50 rounded-xl transition border-2 border-stone-800 hover:border-stone-600"
  >
    <div class="text-middle my-auto">
      <h2 class="color-stone-800 font-bold text-lg">{{ user.name }}</h2>
      <div class="flex gap-2">
        <div class="flex text-stone-400 gap-1">{{ user.gems }} <Gem /></div>
        <div class="flex text-stone-400 gap-1">3 место <Sparkle /></div>
      </div>
    </div>
    <img :src="user.avatar" class="w-[64px] h-[64px] rounded-full" />
  </RouterLink>
</template>
