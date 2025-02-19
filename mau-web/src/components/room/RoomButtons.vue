<script setup lang="ts">
import type { Room } from '@/share/api/types'
import { startGame } from '@/share/api'
import { useUserStore } from '@/share/stores/user'
import { Flame, Link, LogOut, Play } from 'lucide-vue-next'
import { computed } from 'vue'
import HomeButton from '../buttons/HomeButton.vue'

const { room } = defineProps<{ room: Room }>()

const userState = useUserStore()
const me = userState.getMe()
const activeRoom = userState.getActiveRoom()

const canJoin = computed(
  () =>
    !activeRoom.value
    && room.players.length < room.max_players
    && me.value !== null
    && me.value.gems >= room.gems,
)
const canLeave = computed(() => activeRoom.value !== null && room.id === activeRoom.value)
const canStart = computed(
  () =>
    activeRoom.value !== null
    && room.owner.username === userState.userId
    && room.players.length >= room.min_players
    && room.players.length <= room.max_players,
)

async function shareLink() {
  await navigator.clipboard.writeText(window.location.href)
}
</script>

<template>
  <section class="my-8 flex flex-row-reverse flex-wrap gap-4">
    <HomeButton />

    <button
      class="bg-stone-700 p-4 md:p-3 rounded-full transition hover:bg-sky-800"
      @click="shareLink()"
    >
      <Link />
    </button>

    <button
      v-if="canJoin"
      class="bg-stone-700 p-4 md:p-3 rounded-full flex gap-2 transition hover:bg-teal-800"
      @click="userState.joinRoom(room.id)"
    >
      <Flame />
      <div>Зайти</div>
    </button>

    <button
      v-else-if="canLeave"
      class="bg-stone-700 p-4 rounded-full flex gap-2 transition hover:bg-pink-800"
      @click="userState.leaveRoom(room.id)"
    >
      <LogOut :size="24" /> Выйти
    </button>

    <div v-else class="bg-stone-800 p-4 rounded-full flex gap-2">
      <Flame />
      <div>Зайти</div>
    </div>

    <button v-if="canStart" class="bg-stone-700 p-4 rounded-full flex gap-2" @click="startGame">
      <Play :size="24" /> Начать
    </button>
  </section>
</template>
