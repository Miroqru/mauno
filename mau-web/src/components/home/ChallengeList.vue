<script setup lang="ts">
import { getChallenges } from '@/api'
import CardHeader from '@/components/home/CardHeader.vue'
import { ref } from 'vue'
import ChallengeCard from './ChallengeCard.vue' /* PartiallyEnd: #3632/scriptSetup.vue */

const challenges = ref(getChallenges())
</script>

<template>
  <section class="bg-stone-800 p-2 my-2 mb-20 rounded-lg md:align-start md:mb-auto">
    <CardHeader name="Задания дня" to="/challenges" />

    <ChallengeCard v-for="challenge in challenges" :key="challenge.name" :challenge="challenge" />
  </section>
</template>
