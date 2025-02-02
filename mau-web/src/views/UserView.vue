<script setup lang="ts">
import { getUserById } from '@/api'
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import { useUserStore } from '@/stores/user'
import type { User } from '@/types'
import { ref, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import HomeButton from '../components/buttons/HomeButton.vue'
import GetGems from '../components/user/GetGems.vue'
import UserStats from '../components/user/UserStats.vue'

const route = useRoute()

const userStore = useUserStore()
const user: Ref<User | null, User | null> = ref(null)

if (!route.params.id) {
  user.value = userStore.getMe()
} else {
  user.value = getUserById(route.params.id)
}
</script>

<template>
  <UserProfileCard :user="user" />
  <div class="md:flex md:gap-2">
    <UserStats :user="user" class="md:flex-1" />
    <GetGems />
  </div>

  <HomeButton :show-name="true" />
</template>
