<script setup lang="ts">
import { createRoom } from '@/api'
import { useUserStore } from '@/stores/user'
import { Plus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const { showName } = defineProps<{ showName?: boolean }>()
const router = useRouter()
const userState = useUserStore()

async function newRoom() {
  const result = await createRoom(userState.userToken as string)
  if (result.type === 'right') {
    await router.push(`/room/${result.value.id}`)
  }
}
</script>

<template>
  <button
    class="bg-stone-700 p-4 md:p-3 rounded-full flex gap-2 transition hover:bg-stone-600"
    @click="newRoom()"
  >
    <Plus :size="24" />
    <div v-if="showName">
      Комнату
    </div>
  </button>
</template>
[]
