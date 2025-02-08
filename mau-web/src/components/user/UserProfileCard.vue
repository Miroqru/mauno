<script setup lang="ts">
import type { User } from '@/types'
import { getLeaderboardIndex } from '@/api'
import { useUserStore } from '@/stores/user'
import { Gem, Sparkle, User2 } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import LogOutButton from '../buttons/LogOutButton.vue'

const { user } = defineProps<{ user: User }>()
const userStore = useUserStore()
const userTop = ref(0)

onMounted(async () => {
  userTop.value = await getLeaderboardIndex(user.username, 'gems')
})
</script>

<template>
  <section
    class="flex text-center justify-between bg-linear-160 from-pink-400/50 rounded-xl p-2 mb-4"
  >
    <img
      v-if="user.avatar_url"
      :src="user.avatar_url"
      class="w-[128px] h-[128px] rounded-full p-2"
    >
    <User2
      v-else
      :src="user.avatar_url"
      class="w-[128px] h-[128px] rounded-full p-2 text-stone-300"
    />
    <div class="text-middle m-auto">
      <div class="inline-flex gap-2 font-bold text-xl m-2">
        {{ user.name }}<LogOutButton v-if="user.username === userStore.userId" />
      </div>
      <div class="flex text-center gap-4 justify-center text-stone-400">
        <div class="flex gap-1">
          {{ user.gems }} <Gem />
        </div>
        <RouterLink class="flex gap-1" to="/top">
          {{ userTop }} место <Sparkle />
        </RouterLink>
      </div>
    </div>
  </section>
</template>
