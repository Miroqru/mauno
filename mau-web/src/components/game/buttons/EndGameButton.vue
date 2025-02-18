<script setup lang="ts">
import { endGame } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { CircleX } from 'lucide-vue-next'

const userState = useUserStore()

async function endCall() {
  await endGame(userState.userToken as string)
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-amber-500 flex gap-2"
    @click="endCall"
  >
    <CircleX :size="24" />
    <div>Завершить</div>
  </button>
</template>
