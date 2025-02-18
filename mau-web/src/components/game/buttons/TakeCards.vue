<script setup lang="ts">
import { shotgunTake, takeCards } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { BookDown } from 'lucide-vue-next'

const { shotgun } = defineProps<{ shotgun: boolean }>()

const userState = useUserStore()

async function takeCardsCallback() {
  if (shotgun) {
    await shotgunTake(userState.userToken as string)
  }
  else {
    await takeCards(userState.userToken as string)
  }
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full flex gap-2 transition hover:bg-amber-500"
    @click="takeCardsCallback"
  >
    <BookDown :size="24" />
    <div>Взять карты</div>
  </button>
</template>
