<script setup lang="ts">
import type { UserDataIn } from '@/types'
import { loginUser, registerUser } from '@/api'
import { useUserStore } from '@/stores/user'
import { User2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoginButton from './LoginButton.vue'
import RegisterButton from './RegisterButton.vue'

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorBadge = ref(null)

const router = useRouter()
const userState = useUserStore()

const isRegisterActive = computed(() => {
  return (
    username.value !== ''
    && password.value !== ''
    && confirmPassword.value !== ''
    && password.value === confirmPassword.value
  )
})

const isLoginActive = computed(() => {
  return username.value.length > 3 && username.value.length < 16 && password.value.length >= 8
})

const isConfirmActive = computed(() => {
  return password.value.length >= 8
})

async function register(user: UserDataIn) {
  const res = await registerUser(user)
  if (res.error) {
    errorBadge.value = res.data.detail
    username.value = ''
    password.value = ''
    confirmPassword.value = ''
  }
  else {
    await login(user)
  }
}

async function login(user: UserDataIn) {
  const res = await loginUser(user)
  if (res.error) {
    errorBadge.value = res.data.detail
    username.value = ''
    password.value = ''
    confirmPassword.value = ''
  }
  else {
    userState.logIn(user.username, res.data.token)
    await router.push('/home/')
  }
}
</script>

<template>
  <section class="border-2 border-stone-600 p-2 max-w-[400px] mx-auto text-center rounded-xl">
    <h2 class="text-xl mb-4 font-bold">
      Регистрация / вход
    </h2>

    <User2 :size="96" class="align-center mx-auto mb-4 text-stone-100" />

    <div v-if="errorBadge" class="bg-pink-800 p-2 border-2 border-pink-600 rounded-md mv-2">
      {{ errorBadge }}
    </div>

    <form class="mb-2">
      <input
        v-model="username"
        type="text"
        class="focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-xl"
        placeholder="Имя пользователя"
      >

      <input
        v-model="password"
        type="password"
        class="focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-xl"
        placeholder="Пароль"
      >

      <input
        v-if="isConfirmActive"
        v-model="confirmPassword"
        type="password"
        class="focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-xl"
        placeholder="ешё разок пароль?"
      >
    </form>

    <div class="flex gap-2 justify-center mb-2">
      <RegisterButton
        :active="isRegisterActive"
        :user="{ username, password }"
        @submit="register"
      />
      <LoginButton :active="isLoginActive" :user="{ username, password }" @submit="login" />
    </div>

    <div class="text-sm text-stone-400">
      Заходя на сайт вы принимаете политику конфиденциальности и условия использования.
    </div>
  </section>
</template>
