<script setup lang="ts">
import GameButtons from '@/components/game/GameButtons.vue'
import GameChat from '@/components/game/GameChat.vue'
import GamePlayers from '@/components/game/GamePlayers.vue'
import GameTable from '@/components/game/GameTable.vue'
</script>

<template>
  <GamePlayers />
  <GameTable />

  <GameChat />
  <GameButtons />
  <UserCards />
</template>
