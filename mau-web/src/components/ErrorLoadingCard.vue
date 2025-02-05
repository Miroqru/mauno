<script setup lang="ts">
import { WifiOff } from 'lucide-vue-next'

const { details, block } = defineProps<{ details?: object | string; block?: boolean }>()
</script>

<template>
  <div v-if="block" class="text-center p-2 rounded-md border-2 border-stone-700">
    <WifiOff :size="96" class="align-center mx-auto text-pink-100 mb-4" />
    <h1 class="text-xl font-bold text-pink-50 mb-2">Ошибка загрузки</h1>
    <div class="text-stone-300">
      Можно попробовать перезагрузить страницу после или обратиться позже.
    </div>
    <div v-if="details">{{ details }}</div>
  </div>
  <div v-else class="flex gap-4 justify-center">
    <WifiOff :size="32" class="text-pink-100" />
    <div class="text-pink-50 text-lg">{{ details }}</div>
  </div>
</template>
