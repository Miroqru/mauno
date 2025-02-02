<script setup lang="ts">
import { getUserById } from '@/api'
import { CircleX } from 'lucide-vue-next'
import { computed } from 'vue'
import UserStatus from '../home/UserStatus.vue'

const { players } = defineProps<{ players: string[] }>()

const roomPlayers = computed(() => {
  const res = []
  for (const userId of players) {
    const player = getUserById(userId)
    if (player) {
      res.push(player)
    }
  }
  return res
})
</script>

<template>
  <section class="my-4">
    <h2 class="text-xl font-bold">Игроки</h2>

    <div v-for="player in roomPlayers" :key="player.id" class="flex md:inline-flex gap-2">
      <UserStatus class="flex-1" :user="player" />
      <button>
        <CircleX class="text-stone-600 transition hover:text-pink-600" />
      </button>
    </div>
  </section>
</template>
