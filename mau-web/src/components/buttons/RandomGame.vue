<script setup lang="ts">
  import { Shuffle } from 'lucide-vue-next';
</script>

<template>
  <button class="bg-stone-700 fixed p-3 rounded-full bottom-30 right-10">
    <Shuffle :size="20" />
  </button>
</template>
