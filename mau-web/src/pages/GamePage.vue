<script setup lang="ts">
import type { GameContext } from '@/share/api/types'
import type { Ref } from 'vue'
import ErrorLoadingCard from '@/components/ErrorLoadingCard.vue'
import GameButtons from '@/components/game/GameButtons.vue'
import GameChat from '@/components/game/GameChat.vue'
import GameControls from '@/components/game/GameControls.vue'
import GamePlayers from '@/components/game/GamePlayers.vue'
import GameTable from '@/components/game/GameTable.vue'
import UserCards from '@/components/game/UserCards.vue'
import { getGame } from '@/share/api'
import { onMounted, ref } from 'vue'

const gameData: Ref<GameContext | null> = ref(null)

onMounted(async () => {
  gameData.value = await getGame()
})
</script>

<template>
  <div v-if="gameData && gameData.game" class="md:flex md:h-[90vh] justify-around gap-2">
    <div class="flex-1 md:align-center my-auto">
      <GamePlayers :context="gameData" />
      <GameTable :context="gameData" />
    </div>

    <div>
      <GameChat />
      <GameButtons :context="gameData" />
      <UserCards v-if="gameData.player" :player="gameData.player" />
      <GameControls :context="gameData" />
    </div>
  </div>

  <section v-else>
    <div class="text-center justify-between bg-linear-160 from-violet-400/40 rounded-xl p-2 mb-4">
      <h2 class="text-xl mb-2 font-bold">Игра</h2>
      <div class="text-stone-300">Здесь вы можете просмотреть свою статистику.</div>
    </div>
    <ErrorLoadingCard :block="true" />
  </section>
</template>
