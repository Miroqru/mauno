<script setup lang="ts">
import type { OtherPlayer } from '@/share/api/types'
import { kickPlayer } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { User2 } from 'lucide-vue-next'

const { player } = defineProps<{ player: OtherPlayer }>()
const userState = useUserStore()

async function kickCall() {
  await kickPlayer(userState.userToken as string, player.user_id)
}
</script>

<template>
  <button
    class="p-4 rounded-full transition flex gap-2 bg-stone-600 hover:bg-amber-500"
    @click="kickCall"
  >
    <User2 :size="24" />
    <div>выгнать {{ player.name }}</div>
  </button>
</template>
