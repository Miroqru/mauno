<script setup lang="ts">
import type { OtherPlayer } from '@/share/api/types'
import { selectPlayer } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { User2 } from 'lucide-vue-next'

const { player } = defineProps<{ player: OtherPlayer }>()
const userState = useUserStore()

async function selectColorCall() {
  await selectPlayer(userState.userToken as string, player.user_id)
}
</script>

<template>
  <button
    class="p-4 rounded-full transition flex gap-2 bg-stone-600 hover:bg-stone-500"
    @click="selectColorCall"
  >
    <User2 :size="24" />
    <div>{{ player.name }}</div>
    <div>({{ player.hand }})</div>
  </button>
</template>
