<script setup lang="ts">
import { leaveGame } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { DoorOpen } from 'lucide-vue-next'

const userState = useUserStore()

async function leaveCall() {
  await leaveGame(userState.userToken as string)
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-pink-500 flex gap-2"
    @click="leaveCall"
  >
    <DoorOpen :size="24" />
    <div>Выйти</div>
  </button>
</template>
