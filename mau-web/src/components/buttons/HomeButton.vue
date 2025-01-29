<script setup lang="ts">
  import { RouterLink } from 'vue-router';
  import { Home } from 'lucide-vue-next';
</script>

<template>
  <RouterLink to="/" class="bg-stone-800 fixed p-4 rounded-full bottom-10 right-10 flex gap-2">
    <Home :size="24" /> Домой
  </RouterLink>
</template>
