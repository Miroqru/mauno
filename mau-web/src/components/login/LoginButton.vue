<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const { active } = defineProps<{ active: boolean }>()
const userStore = useUserStore()
const router = useRouter()

function logIn() {
  userStore.logIn('m1', 'someToken')
  router.push('/home/')
}
</script>

<template>
  <button
    v-if="active"
    class="bg-stone-700 p-2 rounded-md transition hover:bg-stone-600"
    @click="logIn()"
  >
    Войти
  </button>
  <div v-else class="bg-stone-800 p-2 rounded-md">Войти</div>
</template>
