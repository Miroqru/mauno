<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const { active } = defineProps<{ active: boolean }>()

const userStore = useUserStore()
const router = useRouter()

function logIn() {
  userStore.logIn('a6', 'someToken2')
  router.push('/home/')
}
</script>

<template>
  <button
    v-if="active"
    class="bg-stone-700 p-2 rounded-md transition hover:bg-stone-600"
    @click="logIn()"
  >
    Регистрация
  </button>
  <div v-else class="bg-stone-800 p-2 rounded-md">Регистрация</div>
</template>
