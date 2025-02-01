<script setup lang="ts">
import { Sparkle } from 'lucide-vue-next'
</script>

<template>
  <main
    class="align-center text-center rounded-xl bg-linear-160 from-stone-500 to-stone-800 md:flex md:justify-around"
  >
    <img src="/logo.png" class="w-96 align-center mx-auto" />
    <div class="align-middle my-auto flex-1">
      <h1 class="text-[48px] font-bold mb-2">Mauno</h1>
      <div class="text-lg mb-2">Отличное место чтобы поиграть в классическую карточную игру.</div>
      <div class="p-4 m-4 bg-stone-500 inline-flex rounded-lg hover:bg-stone-600 transition">
        <RouterLink to="/home">Начать игру</RouterLink>
      </div>
    </div>
  </main>

  <section class="m-4 align-center text-center">
    <h2 class="text-xl font-bold mb-4">Крутые фишечки</h2>
    <div class="flex flex-wrap justify-center gap-4">
      <div class="my-2 p-2 bg-stone-800 rounded-md inline-flex gap-4">
        <Sparkle />
        <div>Множество режимов.</div>
      </div>
      <div class="my-2 p-2 bg-stone-800 rounded-md inline-flex gap-4">
        <Sparkle />
        <div>Система рейтинга.</div>
      </div>
      <div class="my-2 p-2 bg-stone-800 rounded-md inline-flex gap-4">
        <Sparkle />
        <div>Играйте в своё удовольствие.</div>
      </div>
    </div>
  </section>
</template>
