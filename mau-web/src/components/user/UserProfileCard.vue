<script setup lang="ts">
import type { User } from '@/types'
import { Gem, Sparkle } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

// TODO: Получение информации о месте в рейтинге

const { user } = defineProps<{
  user: User
}>()
</script>

<template>
  <section
    class="flex text-center justify-between bg-linear-160 from-pink-400/50 rounded-xl p-2 mb-4"
  >
    <img :src="user.avatar" class="w-[128px] h-[128px] rounded-full p-2" />
    <div class="text-middle m-auto">
      <div class="font-bold text-xl m-2">{{ user.name }}</div>
      <div class="flex text-center gap-4 justify-center text-stone-400">
        <div class="flex gap-1">{{ user.gems }} <Gem /></div>
        <RouterLink class="flex gap-1" to="/top">3 место <Sparkle /></RouterLink>
      </div>
    </div>
  </section>
</template>
