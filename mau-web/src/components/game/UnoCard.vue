<script setup lang="ts">
import type { Card } from '@/share/api/types'
import { pushCard } from '@/share/api'

const { card, active } = defineProps<{ card: Card; active: boolean }>()

function getCardImage() {
  const base = active ? 'progressive' : 'progressive_lowsat'
  let color = card.color
  if (card.card_type > 3) {
    color = 4
  }

  return `/${base}/${card.card_type}${color}${card.value}.png`
}
</script>

<template>
  <button
    v-if="active"
    class="inline-flex hover:border-2 transition hover:border-teal-300 rounded-2xl h-[128px]"
    @click="pushCard(card)"
  >
    <img :src="getCardImage()" :alt="getCardImage()" :draggable="true" class="h-[128px]" />
  </button>
  <img v-else :src="getCardImage()" :alt="getCardImage()" class="h-[128px]" />
</template>
