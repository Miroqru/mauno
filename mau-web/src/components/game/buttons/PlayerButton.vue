<script setup lang="ts">
import { selectPlayer } from '@/share/api'
import type { OtherPlayer } from '@/share/api/types'
import { User2 } from 'lucide-vue-next'

const { player } = defineProps<{ player: OtherPlayer }>()
</script>

<template>
  <button
    class="p-4 rounded-full transition flex gap-2 bg-stone-600 hover:bg-stone-500"
    @click="selectPlayer(player.user_id)"
  >
    <User2 :size="24" />
    <div>{{ player.name }}</div>
    <div>({{ player.hand }})</div>
  </button>
</template>
