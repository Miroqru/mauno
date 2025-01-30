<script setup lang="ts">
import GameTable from '../components/game/GameTable.vue'
import GamePlayers from '../components/game/GamePlayers.vue'
import GameChat from '../components/game/GameChat.vue'
import UserCards from '../components/game/UserCards.vue'
import GameButtons from '../components/game/GameButtons.vue'
</script>

<template>
  <GamePlayers />
  <GameTable />
  <GameChat />
  <GameButtons />
  <UserCards />
</template>
