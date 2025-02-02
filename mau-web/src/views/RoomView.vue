<script setup lang="ts">
import { getRoomById } from '@/api'
import RoomButtons from '@/components/room/RoomButtons.vue'
import { useUserStore } from '@/stores/user'
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import RoomModes from '../components/room/RoomModes.vue'
import RoomOwner from '../components/room/RoomOwner.vue'
import RoomPlayers from '../components/room/RoomPlayers.vue'
import RoomSettings from '../components/room/RoomSettings.vue' /* PartiallyEnd: #3632/scriptSetup.vue */

const userState = useUserStore()
const route = useRoute()
const room = ref(getRoomById(route.params.id))
</script>

<template>
  <RoomOwner :room="room" />
  <RoomPlayers :players="room?.players" />

  <div class="md:flex justify-around gap-4">
    <RoomSettings v-if="userState.userId == room?.owner" />
    <RoomModes class="flex-1" />
  </div>

  <RoomButtons :room="room" />
</template>
