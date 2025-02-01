<script setup lang="ts">
import { createRoom } from '@/api'
import { Plus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const { showName } = defineProps<{ showName?: boolean }>()
const router = useRouter()

async function newRoom() {
  const roomId = createRoom()
  await router.push('/room/' + roomId)
}
</script>

<template>
  <button
    class="bg-stone-700 p-4 md:p-3 md:my-2 rounded-full flex gap-2 transition hover:bg-stone-600"
    @click="newRoom()"
  >
    <Plus :size="24" />
    <div v-if="showName">Комнату</div>
  </button>
</template>
