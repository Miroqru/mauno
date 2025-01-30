<script setup lang="ts">
  import { Plus, Shuffle } from 'lucide-vue-next';
</script>

<template>
  <section class="flex justify-around my-4">
    <button class="bg-stone-700  p-4 rounded-full flex gap-2">
      <Plus :size="24" /> Создать
    </button>

    <button class="bg-stone-700  p-4 rounded-full flex gap-2">
      <Shuffle :size="24" /> Случайная
    </button>
  </section>
</template>
