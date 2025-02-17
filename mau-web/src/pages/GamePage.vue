<script setup lang="ts">
import GameButtons from '@/components/game/GameButtons.vue'
import GameChat from '@/components/game/GameChat.vue'
import GamePlayers from '@/components/game/GamePlayers.vue'
import GameTable from '@/components/game/GameTable.vue'
import UserCards from '@/components/game/UserCards.vue'
import { fetchGame } from '@/share/api/api'
import type { ActiveGame } from '@/share/api/types'
import { useUserStore } from '@/share/stores/user'
import { onMounted, ref, type Ref } from 'vue'

const gameData: Ref<ActiveGame | null> = ref(null)
const userState = useUserStore()

onMounted(async () => {
  const res = await fetchGame(userState.userToken as string)
  if (res.type === 'right') {
    gameData.value = res.value
  }
})
</script>

<template>
  <GamePlayers />
  <GameTable />

  <GameChat />
  <GameButtons />
  <UserCards />
</template>
