<script setup lang="ts">
import { getUserById } from '@/api'
import type { Room } from '@/types'
import { Gem, User } from 'lucide-vue-next'
import UserAvatar from '../user/UserAvatar.vue'

const { room } = defineProps<{ room: Room }>()
const owner = getUserById(room.owner)
</script>

<template>
  <RouterLink
    :to="'/room/' + room.id"
    class="flex justify-around m-2 bg-stone-800 p-1 rounded-md transition hover:bg-stone-700"
  >
    <div class="inline-flex gap-2 flex-1">
      <UserAvatar :user="owner" />
      <div class="text-middle m-auto flex-1 font-bold">{{ owner.name }}</div>
    </div>
    <div class="flex gap-1 mr-4 h-[24px] m-auto text-stone-300">
      {{ room.players.length }}/{{ room.maxPlayers }}<User />
    </div>
    <div class="inline-flex gap-1 mr-2 text-middle m-auto text-teal-200">
      {{ room.gems }} <Gem :size="24" />
    </div>
  </RouterLink>
</template>
