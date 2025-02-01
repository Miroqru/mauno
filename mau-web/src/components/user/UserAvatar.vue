<script setup lang="ts">
import type { User } from '@/types'
import { RouterLink } from 'vue-router'

const { user } = defineProps<{ user: User }>()
</script>

<template>
  <RouterLink
    :to="'/user/' + user.id"
    class="transition rounded-full hover:border-2 hover:border-teal-600"
  >
    <img :src="user.avatar" class="w-[32px] h-[32px] rounded-full" />
  </RouterLink>
</template>
