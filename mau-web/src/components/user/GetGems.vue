<script setup lang="ts">
import { Gem, Sparkle } from 'lucide-vue-next';
</script>

<template>
  <section class="md:max-w-[300px] text-center p-2 m-4 rounded-md border-2 border-stone-700 bg-linear-160 from-sky-400/20 to-stone-800">
    <Gem :size="64" class="align-center mx-auto my-2"/>
    <h2 class="text-lg font-bold mb-4">Как зарабатывать гемы</h2>
    <div class="mb-2">
      Как известно гемы используются как основная валюта. <br />
      Есть несколько способов как их можно заработать:
    </div>

    <div class="mb-2">
      <div class="flex gap-2"> <Sparkle /> Играть в игры.</div>
      <div class="flex gap-2"> <Sparkle /> Выполнять задания.</div>
      <div class="flex gap-2"> <Sparkle /> Участвовать в событиях.</div>
      <div class="flex gap-2"> <Sparkle /> Помогать в разработке.</div>
    </div>

    <div>
      последние два действия проходят в нашем прекрасном
      <a href="https://t.me/mili_qlaster" class="text-teal-400 transition hover:text-teal-200">Telegram канал Salormoon</a>!
    </div>

</section>
</template>
