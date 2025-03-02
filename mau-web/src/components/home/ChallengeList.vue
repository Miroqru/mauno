<script setup lang="ts">
import CardHeader from '@/components/home/CardHeader.vue'
import methods from '@/share/api/api'
import { ref } from 'vue'
import ChallengeCard from './ChallengeCard.vue'

const challenges = ref(methods.getChallenges())
</script>

<template>
  <section class="bg-stone-800 p-2 my-2 mb-20 rounded-lg md:align-start md:mb-auto">
    <CardHeader name="Задания дня" to="/challenges" />

    <ChallengeCard v-for="challenge in challenges" :key="challenge.name" :challenge="challenge" />
  </section>
</template>
