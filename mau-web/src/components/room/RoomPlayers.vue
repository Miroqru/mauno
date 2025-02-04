<script setup lang="ts">
import { getUserById } from '@/api'
import type { User } from '@/types'
import { CircleX } from 'lucide-vue-next'
import { ref, watchEffect, type Ref } from 'vue'
import UserStatus from '../home/UserStatus.vue'

const { players, isOwner } = defineProps<{ players: string[]; isOwner: boolean }>()
const roomPlayers: Ref<User[]> = ref([])

watchEffect(async () => {
  const res: User[] = []
  for (const userId of players) {
    const player = await getUserById(userId)
    if (player) {
      res.push(player)
    }
  }
  roomPlayers.value = res
})
</script>

<template>
  <section class="my-4">
    <h2 class="text-xl font-bold">Игроки</h2>

    <div v-for="player in roomPlayers" :key="player.username" class="flex md:inline-flex gap-2">
      <UserStatus class="flex-1" :user="player" />
      <button v-if="isOwner">
        <CircleX class="text-stone-600 transition hover:text-pink-600" />
      </button>
    </div>
  </section>
</template>
