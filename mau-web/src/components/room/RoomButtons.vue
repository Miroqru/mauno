<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import type { Room } from '@/types'
import { Flame, Link, LogOut, Play } from 'lucide-vue-next'
import { computed } from 'vue'
import HomeButton from '../buttons/HomeButton.vue'

const { room } = defineProps<{ room: Room }>()

const userState = useUserStore()
const me = userState.getMe()

const canJoin = computed(
  () =>
    !userState.roomId &&
    room.players.length < room.maxPlayers &&
    me.value != null &&
    me.value.gems >= room.gems,
)
const canLeave = computed(() => userState.roomId != null && room.id == userState.roomId)
const canStart = computed(
  () =>
    userState.roomId != null &&
    room.owner == userState.userId &&
    room.players.length >= room.minPlayers &&
    room.players.length <= room.maxPlayers,
)

console.debug(
  userState.roomId != null,
  room.owner == userState.userId,
  room.players.length >= room.minPlayers,
  room.players.length,
  room.minPlayers,
  room.players.length <= room.maxPlayers,
)

async function shareLink() {
  await navigator.clipboard.writeText(window.location.href)
}
</script>

<template>
  <section class="my-8 flex flex-wrap gap-4">
    <HomeButton />

    <button class="bg-stone-700 p-4 rounded-full transition hover:bg-sky-800" @click="shareLink()">
      <Link />
    </button>

    <button
      class="bg-stone-700 p-4 rounded-full flex gap-2 transition hover:bg-teal-800"
      v-if="canJoin"
      @click="userState.joinRoom(room.id)"
    >
      <Flame />
      <div>Зайти</div>
    </button>

    <button
      v-else-if="canLeave"
      class="bg-stone-700 p-4 rounded-full flex gap-2 transition hover:bg-pink-800"
      @click="userState.leaveRoom()"
    >
      <LogOut :size="24" /> Выйти
    </button>

    <div v-else class="bg-stone-800 p-4 rounded-full flex gap-2">
      <Flame />
      <div>Зайти</div>
    </div>

    <button v-if="canStart" class="bg-stone-700 p-4 rounded-full flex gap-2">
      <Play :size="24" /> Начать
    </button>
  </section>
</template>
