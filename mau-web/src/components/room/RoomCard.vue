<script setup lang="ts">
import type { Room } from '@/share/api/types'
import { Gem, User2 } from 'lucide-vue-next'

const { room } = defineProps<{ room: Room }>()
</script>

<template>
  <section class="my-4 text-center bg-linear-160 from-teal-300/40 rounded-xl p-2 mb-4">
    <RouterLink :to="`/room/${room.id}`">
      <img
        v-if="room.owner.avatar_url"
        :src="room.owner.avatar_url"
        class="w-[128px] h-[128px] rounded-full p-2 align-center mx-auto"
      >
      <User2
        v-else
        :src="room.owner.avatar_url"
        class="w-[128px] h-[128px] rounded-full p-2 align-center mx-auto text-stone-300"
      />

      <div class="text-middle m-auto">
        <div class="font-bold text-xl m-2">
          Комната {{ room.owner.name }}
        </div>
        <div class="flex text-center gap-4 justify-center text-stone-400">
          <div class="flex gap-1">
            {{ room.gems }} <Gem />
          </div>
          <div class="flex gap-1">
            {{ room.players.length }} / {{ room.max_players }} <User2 />
          </div>
        </div>
      </div>
    </RouterLink>
  </section>
</template>
