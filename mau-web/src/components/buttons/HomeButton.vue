<script setup lang="ts">
import { Home } from 'lucide-vue-next'
import { RouterLink } from 'vue-router' /* PartiallyEnd: #3632/scriptSetup.vue */
</script>

<template>
  <RouterLink to="/home/" class="bg-stone-800 fixed p-4 rounded-full bottom-10 right-10 flex gap-2">
    <Home :size="24" /> Домой
  </RouterLink>
</template>
