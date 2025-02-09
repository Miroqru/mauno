<script setup lang="ts">
import type { User } from '@/types'
import type { Ref } from 'vue'
import { getLeaderboardIndex, getUserById } from '@/api'
import ErrorLoadingCard from '@/components/ErrorLoadingCard.vue'
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import UserSettings from '@/components/user/UserSettings.vue'
import { useUserStore } from '@/stores/user'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import HomeButton from '../components/buttons/HomeButton.vue'
import GetGems from '../components/user/GetGems.vue'
import UserStats from '../components/user/UserStats.vue'

const route = useRoute()

const userStore = useUserStore()

let user: Ref<User | null> = ref(null)
const userTop = ref(0)

if (!route.params.id) {
  user = ref(userStore.getMe())
}

onMounted(async () => {
  if (route.params.id) {
    const res = await getUserById(route.params.id as string)
    if (res.type === 'right') {
      user.value = res.value
    }
  }

  if (user.value !== null) {
    const res = await getLeaderboardIndex(user.value.username, 'gems')
    if (res.type === 'right') {
      userTop.value = res.value
    }
  }
})
</script>

<template>
  <div v-if="user">
    <UserProfileCard :user="user" :top-index="userTop" />
    <div class="md:flex md:gap-2">
      <div class="md:flex-1">
        <UserStats :user="user" />
        <UserSettings :user="user" />
      </div>

      <GetGems />
    </div>
  </div>

  <!-- Пока пользователь не успел загрузиться -->
  <section v-else>
    <div class="text-center justify-between bg-linear-160 from-violet-400/40 rounded-xl p-2 mb-4">
      <h2 class="text-xl mb-2 font-bold">
        Профиль пользователя
      </h2>
      <div class="text-stone-300">
        Здесь вы можете просмотреть свою статистику.
      </div>
    </div>
    <ErrorLoadingCard :block="true" />
  </section>

  <section class="p-2 m-2 absolute bottom-0 right-0 flex gap-2">
    <HomeButton :show-name="true" />
  </section>
</template>
