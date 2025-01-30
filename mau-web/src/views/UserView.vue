<script setup lang="ts">
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import HomeButton from '../components/buttons/HomeButton.vue'
import UserStats from '../components/user/UserStats.vue'
import { ref } from 'vue'
import { getMe } from '@/api'

const me = ref(getMe())
</script>

<template>
  <UserProfileCard :user="me" />
  <UserStats :user="me" />

  <HomeButton />
</template>
