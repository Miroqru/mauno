<script setup lang="ts">
import { bluffCard } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { MessageCircleWarning } from 'lucide-vue-next'

const userState = useUserStore()

async function bluffingCall() {
  await bluffCard(userState.userToken as string)
}
</script>

<template>
  <button
    class="bg-stone-600 p-4 rounded-full transition hover:bg-pink-500 flex gap-2"
    @click="bluffingCall"
  >
    <MessageCircleWarning :size="24" />
    <div>Не верю!</div>
  </button>
</template>
