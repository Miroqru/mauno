<script setup lang="ts">
import { joinGame } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { Play } from 'lucide-vue-next'

const userState = useUserStore()

async function joinCall() {
  await joinGame(userState.userToken as string)
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-teal-500 flex gap-2"
    @click="joinCall"
  >
    <Play :size="24" />
    <div>Зайти</div>
  </button>
</template>
