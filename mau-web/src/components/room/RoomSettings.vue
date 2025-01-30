<script setup lang="ts">
import { Circle, CheckCircle } from 'lucide-vue-next'

import RangeSelector from './RangeSelector.vue'
import { ref } from 'vue'

const isPrivate = ref(true)
const maxPlayers = ref(5)
const minPlayers = ref(2)
</script>

<template>
  <section class="my-4">
    <h2 class="text-xl font-bold mb-2">Настройки комнаты</h2>

    <div class="flex gap-2 mb-2">
      <button @click="isPrivate = !isPrivate">
        <CheckCircle v-if="isPrivate" class="text-teal-200" />
        <Circle v-else />
      </button>
      <div>Приватная комната</div>
    </div>

    <div class="mb-2 justify-between flex">
      <div>Максимум игроков</div>
      <RangeSelector :value="maxPlayers" />
    </div>

    <div class="mb-2 justify-between flex">
      <div>Минимум игроков</div>
      <RangeSelector :value="minPlayers" />
    </div>
  </section>
</template>
