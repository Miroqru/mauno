<template>
  <main
    class="align-center text-center rounded-xl bg-linear-160 from-stone-500 to-stone-800 md:flex md:justify-around"
  >
    <img src="/logo.png" class="w-96 align-center mx-auto" />
    <div class="align-middle my-auto flex-1">
      <h1 class="text-[48px] font-bold mb-2">Mauno</h1>
      <div class="text-lg mb-2">Отличное место чтобы поиграть в классическую карточную игру.</div>
      <div
        class="p-4 m-4 bg-stone-500 inline-flex rounded-lg hover:bg-stone-600 transition shadow-xl"
      >
        <RouterLink to="/home"> Начать игру </RouterLink>
      </div>
    </div>
  </main>
</template>
