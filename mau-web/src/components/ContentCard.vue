<script setup lang="ts">
  import CardHeader from './CardHeader.vue';

  const props = defineProps<{
    name: string
    to: string
  }>()
</script>

<template>
  <section class="bg-stone-800 p-2 m-2 rounded-lg">
    <CardHeader :name="props.name" :to="props.to" />
  </section>
</template>
