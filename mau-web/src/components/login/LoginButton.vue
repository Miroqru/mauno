<script setup lang="ts">
import type { UserDataIn } from '@/share/api/types'

const { active, user } = defineProps<{ active: boolean, user: UserDataIn }>()
const emit = defineEmits<{ submit: [UserDataIn] }>()
</script>

<template>
  <button
    v-if="active"
    class="bg-teal-700 p-2 rounded-md transition hover:bg-teal-600 flex-1"
    @click="emit('submit', user)"
  >
    Войти
  </button>
  <div v-else class="bg-stone-800 p-2 rounded-md flex-1">
    Войти
  </div>
</template>
