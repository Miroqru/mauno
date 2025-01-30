<script setup lang="ts">
  import { BookDown } from 'lucide-vue-next';
</script>

<template>
  <button class="bg-stone-600 p-4 rounded-full flex gap-2">
    <BookDown :size="24" />
    <div>Взять карты</div>
  </button>
</template>
