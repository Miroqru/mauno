<script setup lang="ts">
import { Home } from 'lucide-vue-next'
import { RouterLink } from 'vue-router' /* PartiallyEnd: #3632/scriptSetup.vue */
const { showName } = defineProps<{ showName?: boolean }>()
</script>

<template>
  <RouterLink
    to="/home/"
    class="bg-stone-700 p-4 rounded-full flex gap-2 transition hover:bg-stone-600"
  >
    <Home :size="24" />
    <div v-if="showName">Домой</div>
  </RouterLink>
</template>
