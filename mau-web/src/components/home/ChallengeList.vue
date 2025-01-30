<script setup lang="ts">
import CardHeader from '@/components/CardHeader.vue'
import LobbyCard from './LobbyCard.vue'
import ChallengeCard from './ChallengeCard.vue'
</script>

<template>
  <section class="bg-stone-800 p-2 m-2 rounded-lg">
    <CardHeader name="Задания дня" to="/challenges" />

    <ChallengeCard desc="Сыграть 5 раз" :now="2" :total="5" :reward="15" />

    <ChallengeCard desc="Сыграть 70 карт" :now="38" :total="70" :reward="50" />

    <ChallengeCard desc="Выбросить пару +2 подряд" :now="2" :total="7" :reward="120" />
  </section>
</template>
