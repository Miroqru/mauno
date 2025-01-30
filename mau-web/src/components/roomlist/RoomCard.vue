<script setup lang="ts">
import { Gem } from 'lucide-vue-next'

const props = defineProps<{
  name: string
  avatarUrl: string
  players: number
  maxPlayers: number
  crystals: number
}>()
</script>

<template>
  <div class="flex justify-around m-2 bg-stone-800 p-2 rounded-lg">
    <div class="inline-flex gap-2 flex-1">
      <img :src="props.avatarUrl" class="w-[32px] h-[32px] rounded-full" />
      <div class="text-middle m-auto flex-1 font-bold">{{ props.name }}</div>
    </div>
    <div class="mr-4 h-[24px] m-auto text-stone-300">
      {{ props.players }}/{{ props.maxPlayers }}
    </div>
    <div class="inline-flex gap-1 mr-2 text-middle m-auto text-teal-200">
      {{ props.crystals }} <Gem :size="24" />
    </div>
  </div>
</template>
