<script setup lang="ts">
import { getUserById } from '@/api'
import ErrorLoadingCard from '@/components/ErrorLoadingCard.vue'
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import UserSettings from '@/components/user/UserSettings.vue'
import { useUserStore } from '@/stores/user'
import type { User } from '@/types'
import { onMounted, ref, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import HomeButton from '../components/buttons/HomeButton.vue'
import GetGems from '../components/user/GetGems.vue'
import UserStats from '../components/user/UserStats.vue'

const route = useRoute()

const userStore = useUserStore()

let user: Ref<User | null> = ref(null)

if (!route.params.id) {
  user = ref(userStore.getMe())
}

onMounted(async () => {
  if (route.params.id) {
    user.value = await getUserById(route.params.id as string)
  }
})
</script>

<template>
  <div v-if="user">
    <UserProfileCard :user="user" />
    <div class="md:flex md:gap-2">
      <div class="md:flex-1">
        <UserStats :user="user" />
        <UserSettings :user="user" />
      </div>

      <GetGems />
    </div>
  </div>

  <!-- Пока пользователь не успел загрузиться -->
  <section
    v-else
    class="text-center justify-between bg-linear-160 from-violet-400/40 rounded-xl p-2 mb-4"
  >
    <h2 class="text-xl mb-2 font-bold">Профиль пользователя</h2>
    <div class="text-stone-300">Здесь вы можете просмотреть свою статистику.</div>
  </section>
  <ErrorLoadingCard :block="true" />

  <section class="p-2 m-2 fixed bottom-0 right-0 flex gap-2">
    <HomeButton :show-name="true" />
  </section>
</template>
