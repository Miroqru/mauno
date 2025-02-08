<script setup lang="ts">
import type { User } from '@/types'
import { User2 } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const { user } = defineProps<{ user: User }>()
</script>

<template>
  <RouterLink
    :to="`/user/${user.username}`"
    class="transition rounded-full hover:border-2 hover:border-teal-600"
  >
    <img v-if="user.avatar_url" :src="user.avatar_url" class="w-[32px] h-[32px] rounded-full">
    <User2 v-else class="w-[32px] h-[32px] rounded-full text-stone-500" />
  </RouterLink>
</template>
