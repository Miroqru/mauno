<script setup lang="ts">
import type { Category } from '@/api'
import type { User } from '@/types'
import { Book, Gamepad2, Gem, Sparkle } from 'lucide-vue-next'
import UserAvatar from '../user/UserAvatar.vue'

const { index, user, displayParam } = defineProps<{
  index?: number
  user: User
  displayParam?: Category
}>()
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

    <div
      v-if="displayParam == 'games'"
      class="inline-flex gap-1 mr-2 text-middle m-auto text-teal-200"
    >
      {{ user.gems }} <Gamepad2 :size="24" />
    </div>
    <div
      v-else-if="displayParam == 'wins'"
      class="inline-flex gap-1 mr-2 text-middle m-auto text-amber-200"
    >
      {{ user.gems }} <Sparkle :size="24" />
    </div>
    <div
      v-else-if="displayParam == 'cards'"
      class="inline-flex gap-1 mr-2 text-middle m-auto text-pink-200"
    >
      {{ user.gems }} <Book :size="24" />
    </div>

    <div v-else class="inline-flex gap-1 mr-2 text-middle m-auto text-sky-200">
      {{ user.gems }} <Gem :size="24" />
    </div>
  </RouterLink>
</template>
