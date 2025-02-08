<script setup lang="ts">
import { getRandomRoom } from '@/api'
import { Shuffle } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const { showName } = defineProps<{ showName?: boolean }>()
const router = useRouter()

async function randomRoom() {
  const result = await getRandomRoom()
  if (result.error) {
    console.error(result.data)
  }
  else {
    await router.push(`/room/${result.data.id}`)
  }
}
</script>

<template>
  <button
    class="bg-stone-700 p-4 md:p-3 rounded-full flex gap-2 transition hover:bg-stone-600"
    @click="randomRoom()"
  >
    <Shuffle :size="24" />
    <div v-if="showName">
      Случайная
    </div>
  </button>
</template>
