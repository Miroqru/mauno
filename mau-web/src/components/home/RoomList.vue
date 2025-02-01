<script setup lang="ts">
import { getRooms } from '@/api'
import { ref } from 'vue'
import RoomCard from '../roomlist/RoomCard.vue'
import CardHeader from './CardHeader.vue'

const rooms = ref(getRooms())
</script>

<template>
  <section class="p-2 my-2">
    <CardHeader name="Открытые комнаты" to="/rooms" />
    <RoomCard v-for="room in rooms" :key="room.id" :room="room" />
  </section>
</template>
