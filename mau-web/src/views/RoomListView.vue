<script setup lang="ts">
import HomeButton from '@/components/buttons/HomeButton.vue';
import RoomButtons from '../components/roomlist/RoomButtons.vue';
import GameRooms from '../components/roomlist/GameRooms.vue';

</script>

<template>
  <section class="text-center justify-between bg-linear-160 from-teal-300/40 rounded-xl p-2 mb-4">
    <h2 class="text-xl mb-2 font-bold">Игровые комнаты</h2>
    <div class="text-stone-3003">Место, где игроки собираются вместе поиграть.</div>
  </section>

  <RoomButtons />
  <GameRooms />

  <HomeButton />
</template>
