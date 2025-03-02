<script setup lang="ts">
import type { User } from '@/share/api/types'

const { user } = defineProps<{ user: User }>()
</script>

<template>
  <section class="p-2 rounded-md bg-stone-800">
    <h2 class="font-bold text-xl text-center">Подробнее о пользователе</h2>

    <div class="flex justify-between p-2">
      <div>Короткое имя</div>
      <div>{{ user.username }}</div>
    </div>

    <div class="flex justify-between p-2">
      <div>Всего игр</div>
      <div>{{ user.play_count }}</div>
    </div>

    <div class="flex justify-between p-2">
      <div>Побед</div>
      <div>{{ user.win_count }}</div>
    </div>

    <div class="flex justify-between p-2">
      <div>Разыграно карт</div>
      <div>{{ user.cards_count }}</div>
    </div>
  </section>
</template>
