<script setup lang="ts">
import HomeButton from '../buttons/HomeButton.vue'
import NewGame from '../buttons/NewGame.vue'
import RandomGame from '../buttons/RandomGame.vue'

const { mobile } = defineProps<{ mobile: boolean }>()
</script>

<template>
  <section v-if="mobile" class="flex justify-around my-4">
    <NewGame :show-name="true" />
    <RandomGame :show-name="true" />
  </section>
  <section v-else class="flex gap-2 flex-col p-2 border-2 border-stone-700 rounded-md">
    <HomeButton :show-name="true" />
    <NewGame :show-name="true" />
    <RandomGame :show-name="true" />
  </section>
</template>
