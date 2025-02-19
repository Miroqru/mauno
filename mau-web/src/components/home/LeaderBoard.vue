<script setup lang="ts">
import CardHeader from '@/components/home/CardHeader.vue'
import { getRating } from '@/share/api'
import type { User } from '@/share/api/types'
import type { Ref } from 'vue'
import { onMounted, ref } from 'vue'
import ErrorLoadingCard from '../ErrorLoadingCard.vue'
import UserStatus from './UserStatus.vue'

const gemsTop: Ref<User[]> = ref([])

onMounted(async () => {
  gemsTop.value = await getRating('gems')
})
</script>

<template>
  <section class="p-2 my-2 md:rounded-md md:border-3 md:border-stone-700">
    <CardHeader name="Лучшие игроки" to="/top" />
    <div v-if="gemsTop.length" class="md:grid md:grid-cols-2 lg:grid-cols-3 md:justify-stretch">
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
