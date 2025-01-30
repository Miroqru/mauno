<script setup lang="ts">
import RoomButtons from '@/components/room/RoomButtons.vue'
import RoomOwner from '../components/room/RoomOwner.vue'
import RoomPlayers from '../components/room/RoomPlayers.vue'
import RoomSettings from '../components/room/RoomSettings.vue'
import RoomModes from '../components/room/RoomModes.vue'
</script>

<template>
  <RoomOwner />
  <RoomPlayers />
  <RoomSettings />
  <RoomModes />

  <RoomButtons />
</template>
