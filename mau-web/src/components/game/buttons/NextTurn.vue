<script setup lang="ts">
import { nextTurn } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { ChevronRightCircle } from 'lucide-vue-next'

const userState = useUserStore()

async function nextTurnCallback() {
  await nextTurn(userState.userToken as string)
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-teal-500 flex gap-2"
    @click="nextTurnCallback"
  >
    <ChevronRightCircle :size="24" />
    <div>Следующий ход</div>
  </button>
</template>
