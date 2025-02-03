<script setup lang="ts">
import type { User } from '@/types'
import { Gem } from 'lucide-vue-next'
import UserAvatar from '../user/UserAvatar.vue'

const { index, user } = defineProps<{ index?: number; user: User }>()
</script>

<template>
  <RouterLink
    :to="'/user/' + user.username"
    class="flex gap-2 justify-around m-2 bg-stone-800 p-1 rounded-md transition hover:bg-stone-700"
  >
    <div v-if="index" class="text-amber-50 text-middle my-auto">{{ index }}</div>
    <div class="inline-flex gap-2 flex-1">
      <UserAvatar :user="user" />
      <div class="text-middle m-auto flex-1 font-bold text-amber-503">
        {{ user.name }}
      </div>
    </div>
    <div class="inline-flex gap-1 mr-2 text-middle m-auto text-amber-200">
      {{ user.gems }} <Gem :size="24" />
    </div>
  </RouterLink>
</template>
