<script setup lang="ts">
import type { GameContext } from '@/share/api/types'
import { computed } from 'vue'
import EndGameButton from './buttons/EndGameButton.vue'
import JoinButton from './buttons/JoinButton.vue'
import KickPlayerButton from './buttons/KickPlayerButton.vue'
import LeaveButton from './buttons/LeaveButton.vue'
import SkipButton from './buttons/SkipButton.vue'

const { context } = defineProps<{ context: GameContext }>()

const isOwner = computed(() => context.game?.owner_id == context.player?.user_id)
</script>

<template>
  <section v-if="context.game" class="flex flex-row-reverse gap-4 my-4">
    <SkipButton v-if="isOwner" />
    <EndGameButton v-if="isOwner" />
    <LeaveButton v-if="context.player" />
    <JoinButton v-else />
  </section>
  <div
    v-if="isOwner && context.game"
    class="flex flex-wrap justify-around gap-2 border-2 border-stone-700 rounded-md p-2"
  >
    <KickPlayerButton
      v-for="player in context.game.players"
      :key="player.user_id"
      :player="player"
    />
  </div>
</template>
