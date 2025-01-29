<script setup lang="ts">
  import CardHeader from '@/components/CardHeader.vue';
import LobbyCard from './LobbyCard.vue';
</script>

<template>
  <section class="bg-stone-800 p-2 m-2 rounded-lg">
    <CardHeader name="Сейчас играют" to="/lobby" />

    <LobbyCard />
    <LobbyCard />
    <LobbyCard />
    <LobbyCard />
    <LobbyCard />
  </section>
</template>
