<script setup lang="ts">
import { selectColor } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { Sparkle } from 'lucide-vue-next'

const { color, colorName } = defineProps<{ color: number, colorName: string }>()
const userState = useUserStore()

async function selectColorCall() {
  await selectColor(userState.userToken as string, color)
}
</script>

<template>
  <button
    class="p-4 rounded-full transition flex gap-2 bg-stone-600 hover:bg-stone-500"
    @click="selectColorCall"
  >
    <Sparkle :size="24" />
    <div>{{ colorName }}</div>
  </button>
</template>
