<script setup lang="ts">
import { getLeaders } from '@/api'
import CardHeader from '@/components/home/CardHeader.vue'
import type { User } from '@/types'
import { onMounted, ref, type Ref } from 'vue'
import ErrorLoadingCard from '../ErrorLoadingCard.vue'
import UserStatus from './UserStatus.vue'

const gemsTop: Ref<User[] | null> = ref(null)

onMounted(async () => {
  gemsTop.value = await getLeaders('gems')
})
</script>

<template>
  <section class="p-2 my-2 md:rounded-md md:border-3 md:border-stone-700">
    <CardHeader name="Лучшие игроки" to="/top" />
    <div v-if="gemsTop" class="md:grid md:grid-cols-2 lg:grid-cols-3 md:justify-stretch">
      <UserStatus
        v-for="[index, user] in gemsTop.slice(0, 5).entries()"
        :key="user.username"
        :user="user"
        :index="index + 1"
      />
    </div>
    <ErrorLoadingCard v-else class="text-center" details="А где таблица лидеров?" />
  </section>
</template>
