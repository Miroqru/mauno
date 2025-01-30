<script setup lang="ts">
  import { DoorOpen, Play } from 'lucide-vue-next';
</script>

<template>
  <section class="my-8 flex justify-around">
    <button class="bg-stone-700 p-4 rounded-full flex gap-2">
      <DoorOpen :size="24" /> Выйти
    </button>

    <button class="bg-stone-700  p-4 rounded-full flex gap-2">
      <Play :size="24" /> Начать
    </button>
  </section>
</template>
