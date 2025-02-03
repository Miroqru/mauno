<script setup lang="ts">
import { getTopGems } from '@/api'
import CardHeader from '@/components/home/CardHeader.vue'
import { ref } from 'vue'
import UserStatus from './UserStatus.vue' /* PartiallyEnd: #3632/scriptSetup.vue */

const gemsTop = ref(getTopGems())
</script>

<template>
  <section class="p-2 my-2 md:rounded-md md:border-3 md:border-stone-700">
    <CardHeader name="Лучшие игроки" to="/top" />
    <div class="md:grid md:grid-cols-2 lg:grid-cols-3 md:justify-stretch">
      <UserStatus
        v-for="[index, user] in gemsTop.slice(0, 5).entries()"
        :key="user.username"
        :user="user"
        :index="index + 1"
      />
    </div>
  </section>
</template>
