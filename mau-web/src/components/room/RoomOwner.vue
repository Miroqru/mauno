<script setup lang="ts">
import type { Room } from '@/share/api/types'
import { Gem, User2 } from 'lucide-vue-next'

const { room } = defineProps<{ room: Room }>()
</script>

<template>
  <section
    class="flex text-center justify-between bg-linear-160 from-teal-300/40 rounded-xl p-2 mb-4"
  >
    <div class="text-middle m-auto">
      <div class="font-bold text-xl m-2">
        {{ room.name }}
      </div>
      <div class="flex flex-wrap text-center gap-4 justify-center text-stone-400">
        <div>Создал {{ room.owner.name }}</div>
        <div class="flex gap-1">
          {{ room.gems }} <Gem />
        </div>
        <div class="flex gap-1">
          {{ room.players.length }} / {{ room.max_players }} <User2 />
        </div>
      </div>
    </div>
    <img
      v-if="room.owner.avatar_url"
      :src="room.owner.avatar_url"
      class="w-[128px] h-[128px] rounded-full p-2"
    >
    <User2 v-else class="w-[128px] h-[128px] rounded-full p-2 text-stone-400" />
  </section>
</template>
