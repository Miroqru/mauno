<script setup lang="ts">
import type { GameContext, User } from '@/share/api/types'
import type { Ref } from 'vue'
import { getUser } from '@/share/api'
import { User2 } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'

const { game } = defineProps<{ game: GameContext }>()
const owner: Ref<User | null> = ref(null)

onMounted(async () => {
  if (game.game !== null) {
    owner.value = await getUser(game.game?.owner_id)
  }
})
</script>

<template>
  <section v-if="game.game" class="my-4 bg-linear-160 from-emerald-300/40 rounded-xl p-2 mb-4">
    <RouterLink to="/game" class="flex justify-between">
      <img
        v-if="owner && owner.avatar_url"
        :src="owner.avatar_url"
        class="w-[128px] h-[128px] rounded-full p-2 align-center mx-auto"
      />
      <User2
        v-else
        class="w-[128px] h-[128px] rounded-full p-2 align-center mx-auto text-stone-300"
      />

      <div class="text-middle m-auto">
        <div class="font-bold text-xl m-2">Игра началась</div>
        <div class="font-bold text-xl m-2">Скорее заходите!</div>
      </div>
    </RouterLink>
  </section>
</template>
