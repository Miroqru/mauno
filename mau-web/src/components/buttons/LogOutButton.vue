<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { LogOut } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

function logOut() {
  userStore.logOut()
  router.push('/')
}
</script>

<template>
  <button class="flex gap-2 transition hover:bg-stone-600" @click="logOut()">
    <LogOut :size="18" />
  </button>
</template>
