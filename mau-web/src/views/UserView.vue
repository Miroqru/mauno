<script setup lang="ts">
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import HomeButton from '../components/buttons/HomeButton.vue'
import UserStats from '../components/user/UserStats.vue'
import { ref } from 'vue'
import { getMe } from '@/api'
import GetGems from '../components/user/GetGems.vue'

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
