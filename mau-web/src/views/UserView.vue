<script setup lang="ts">
import { getMe } from '@/api'
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import { ref } from 'vue'
import HomeButton from '../components/buttons/HomeButton.vue'
import GetGems from '../components/user/GetGems.vue'
import UserStats from '../components/user/UserStats.vue'

const me = ref(getMe())
</script>

<template>
  <UserProfileCard :user="me" />
  <div class="md:flex md:gap-2">
    <UserStats :user="me" class="md:flex-1" />
    <GetGems />
  </div>

  <HomeButton />
</template>
