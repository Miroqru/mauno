<script setup lang="ts">
import ChatMessage from '@/components/game/ChatMessage.vue'

const messages = [
  { name: 'Milinuri', message: 'Выбросил карту +2' },
  { name: 'Qq Uwu', message: 'Беру 2 карты' },
  { name: 'Qq Uwu', message: 'Пропускаю' },
  { name: 'Miroq', message: 'Выбрасываю синий пропуск хода' },
  { name: 'Qq Uwu', message: 'Выбрасываю +2' },
  { name: 'Miroq', message: 'Выбрасываю +2' },
  { name: 'Milinuri', message: 'Беру 4 карты.' },
  { name: 'Milinuri', message: 'Пропускаю ход.' },
]
</script>

<template>
  <section class="bg-stone-950 p-2 m-4 rounded-xl h-[20vh] md:h-[30vh] overflow-y-auto">
    <ChatMessage
      v-for="[index, message] in messages.entries()"
      :key="index"
      :name="message.name"
      :message="message.message"
    />
  </section>
</template>
