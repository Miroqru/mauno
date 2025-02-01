<script setup lang="ts">
import { createRoom } from '@/api'
import { Shuffle } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const { showName } = defineProps<{ showName?: boolean }>()
const router = useRouter()

async function randomRoom() {
  const roomId = createRoom()
  await router.push('/room/' + roomId)
}
</script>

<template>
  <button
    class="bg-stone-700 p-4 md:p-3 md:my-2 rounded-full flex gap-2 transition hover:bg-stone-600"
    @click="randomRoom()"
  >
    <Shuffle :size="24" />
    <div v-if="showName">Случайная</div>
  </button>
</template>
