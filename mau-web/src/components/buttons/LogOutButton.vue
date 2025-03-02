<script setup lang="ts">
import { useUserStore } from '@/share/stores/user'
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
  <button class="flex gap-2 transition hover:text-stone-400" @click="logOut()">
    <LogOut :size="18" />
  </button>
</template>
