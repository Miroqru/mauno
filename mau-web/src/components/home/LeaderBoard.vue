<script setup lang="ts">
  import CardHeader from '@/components/CardHeader.vue';
import UserStatus from './UserStatus.vue';
</script>

<template>
  <section class="bg-stone-800 p-2 m-2 rounded-lg">
    <CardHeader name="Лучшие игроки" to="/top" />

    <UserStatus name="Qq Uwu" :gems="3578" />
    <UserStatus name="Miroq" :gems="1724" />
    <UserStatus name="Milinuri" :gems="100" />
  </section>
</template>
