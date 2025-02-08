<script setup lang="ts">
import type { Room, User } from '@/types'
import { kickUserFromRoom, setOwnerInRoom } from '@/api'
import { useUserStore } from '@/stores/user'
import { CircleX, Crown } from 'lucide-vue-next'
import UserStatus from '../home/UserStatus.vue'

const { room } = defineProps<{ room: Room }>()
const userState = useUserStore()

async function kick(user: User) {
  await kickUserFromRoom(userState.userToken as string, room.id, user.username)
}
async function setOwner(user: User) {
  await setOwnerInRoom(userState.userToken as string, room.id, user.username)
}
</script>

<template>
  <section class="my-4">
    <h2 class="text-xl font-bold">
      Игроки
    </h2>

    <div v-for="player in room.players" :key="player.username" class="flex md:inline-flex gap-1">
      <Crown
        v-if="player.username === room.owner.username"
        class="align-middle my-auto text-amber-300"
      />
      <UserStatus class="flex-1" :user="player" />
      <button
        v-if="userState.userId === room.owner.username && player.username !== room.owner.username"
        @click="kick(player)"
      >
        <CircleX class="text-stone-600 transition hover:text-pink-600" />
      </button>
      <button
        v-if="userState.userId === room.owner.username && player.username !== room.owner.username"
        @click="setOwner(player)"
      >
        <Crown class="text-stone-600 transition hover:text-amber-500" />
      </button>
    </div>
  </section>
</template>
