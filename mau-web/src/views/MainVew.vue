<script setup lang="ts">
import FeatureCard from '../components/lending/FeatureCard.vue' /* PartiallyEnd: #3632/scriptSetup.vue */
import ProjectRoadmap from '../components/lending/ProjectRoadmap.vue' /* PartiallyEnd: #3632/scriptSetup.vue */
import UnoMain from '../components/lending/UnoMain.vue'

// TODO: Ну написать что-нибудь более убедительное блин
const features = [
  {
    name: 'Множество режимов',
    desc: 'Когда обычные картишки уже надоели, как насчёт того чтобы внести немного больше суеты.',
  },
  {
    name: 'Рейтинговая система',
    desc: 'Соревнуйтесь с другими игроками за звание лучшего игрока.',
  },
  {
    name: 'Играйте в своё удовольствие',
    desc: 'Создавайте свои собственные комнаты и приглашайте друзей.',
  },
  {
    name: 'Открытость',
    desc: 'Проект существует за счёт вашей поддержки.',
  },
]
</script>

<template>
  <UnoMain />

  <section class="m-4 align-center text-center">
    <h2 class="text-xl font-bold mb-4">Крутые фишечки</h2>
    <div class="justify-center gap-4">
      <FeatureCard v-for="feat in features" :key="feat.name" :name="feat.name" :desc="feat.desc" />
    </div>
  </section>

  <ProjectRoadmap />
</template>
