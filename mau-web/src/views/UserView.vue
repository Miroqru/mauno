<script setup lang="ts">
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import { useUserStore } from '@/stores/user'
import { ref } from 'vue'
import HomeButton from '../components/buttons/HomeButton.vue'
import GetGems from '../components/user/GetGems.vue'
import UserStats from '../components/user/UserStats.vue'

const userStore = useUserStore()
const me = ref(userStore.getMe())
</script>

<template>
  <UserProfileCard :user="me" />
  <div class="md:flex md:gap-2">
    <UserStats :user="me" class="md:flex-1" />
    <GetGems />
  </div>

  <HomeButton />
</template>
