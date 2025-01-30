<script setup lang="ts">
import type { User } from '@/types';

const {user} = defineProps<{
  user: User
}>()
</script>

<template>
  <section class="p-2 rounded-md bg-stone-800">
    <h2 class="font-bold text-xl text-center">Статистика пользователя</h2>

    <div class="flex justify-between p-2">
      <div>Всего игр</div>
      <div>{{ user.playCount }}</div>
    </div>

    <div class="flex justify-between p-2">
      <div>Побед</div>
      <div>{{ user.winCount }}</div>
    </div>

    <div class="flex justify-between p-2">
      <div>Разыграно карт</div>
      <div>{{ user.cardsCount }}</div>
    </div>
  </section>
</template>
