<script setup lang="ts">
import { shotgunShot } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { Flame } from 'lucide-vue-next'

const userState = useUserStore()

async function shotgunCall() {
  await shotgunShot(userState.userToken as string)
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-pink-500 flex gap-2"
    @click="shotgunCall"
  >
    <Flame :size="24" />
    <div>Следующий ход</div>
  </button>
</template>
