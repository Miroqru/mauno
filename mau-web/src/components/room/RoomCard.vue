<script setup lang="ts">
import { getUserById } from '@/api'
import type { Room } from '@/types'
import { Gem, User } from 'lucide-vue-next'
import { ref } from 'vue'

const { room } = defineProps<{ room: Room }>()
const owner = ref(getUserById(room.owner))
</script>

<template>
  <section class="text-center bg-linear-160 from-teal-300/40 rounded-xl p-2 mb-4">
    <RouterLink :to="'/room/' + room.id">
      <img :src="owner?.avatar" class="w-[128px] h-[128px] rounded-full p-2 align-center mx-auto" />
      <div class="text-middle m-auto">
        <div class="font-bold text-xl m-2">Комната {{ owner?.name }}</div>
        <div class="flex text-center gap-4 justify-center text-stone-400">
          <div class="flex gap-1">{{ room.gems }} <Gem /></div>
          <div class="flex gap-1">{{ room.players.length }} / {{ room.maxPlayers }} <User /></div>
        </div>
      </div>
    </RouterLink>
  </section>
</template>
