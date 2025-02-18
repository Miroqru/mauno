<script setup lang="ts">
import { skipPlayer } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { StepForward } from 'lucide-vue-next'

const userState = useUserStore()

async function skipCall() {
  await skipPlayer(userState.userToken as string)
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-violet-700 flex gap-2"
    @click="skipCall"
  >
    <StepForward :size="24" />
  </button>
</template>
