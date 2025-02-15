<script setup lang="ts">
import HomeButton from '@/components/buttons/HomeButton.vue'
import { getChallenges } from '@/share/api/api'
import ChallengeCard from '../components/home/ChallengeCard.vue'

const challenges = getChallenges()
</script>

<template>
  <section class="text-center justify-between bg-linear-160 from-rose-400/40 rounded-xl p-2 mb-4">
    <h2 class="text-xl mb-2 font-bold">
      Ежедневные задания
    </h2>
    <div class="text-stone-300">
      За их выполнение можно получать кристаллы.
    </div>
  </section>

  <section class="border-2 border-stone-700 rounded-md">
    <ChallengeCard v-for="challenge in challenges" :key="challenge.name" :challenge="challenge" />
  </section>

  <section class="p-2 m-2 absolute bottom-0 right-0 flex gap-2">
    <HomeButton :show-name="true" />
  </section>
</template>
