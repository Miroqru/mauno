<script setup lang="ts">
import type { UserDataIn } from '@/share/api/types'

const { active, user } = defineProps<{ active: boolean; user: UserDataIn }>()
const emit = defineEmits<{ submit: [UserDataIn] }>()
</script>

<template>
  <button
    v-if="active"
    class="bg-stone-700 p-2 rounded-md transition hover:bg-stone-600"
    @click="emit('submit', user)"
  >
    Регистрация
  </button>
</template>
