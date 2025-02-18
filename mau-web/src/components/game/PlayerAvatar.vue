<script setup lang="ts">
import { getUser } from '@/share/api'
import type { OtherPlayer, User } from '@/share/api/types'
import { User2 } from 'lucide-vue-next'
import type { Ref } from 'vue'
import { onMounted, ref } from 'vue'
import Counter from './Counter.vue'

const { player, active } = defineProps<{
  active: boolean
  player: OtherPlayer
}>()

const user: Ref<User | null> = ref(null)

onMounted(async () => {
  user.value = await getUser(player.user_id)
})
</script>

<template>
  <div>
    <div
      class="w-[64px] h-[64px] border-2 rounded-full border-stone-400 relative"
      :class="{ 'border-teal-300': active }"
    >
      <img
        v-if="user && user.avatar_url"
        :src="user.avatar_url"
        class="w-[64px] h-[64px] rounded-full"
      />
      <User2 v-else class="w-[52px] h-[52px] text-stone-500 relative" :stroke-width="1" />
      <Counter :value="player.hand" />
    </div>
    <div class="text-center">
      {{ player.name }}
    </div>
  </div>
</template>
