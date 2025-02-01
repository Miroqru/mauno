<script setup lang="ts">
import { computed, ref } from 'vue'
import LoginButton from './LoginButton.vue'
import RegisterButton from './RegisterButton.vue'

const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const isRegisterActive = computed(() => {
  return (
    email.value != '' &&
    password.value != '' &&
    confirmPassword.value != '' &&
    password.value == confirmPassword.value
  )
})

const isLoginActive = computed(() => {
  return email.value != '' && password.value != ''
})
</script>

<template>
  <section class="border-2 border-stone-600 p-2 max-w-[400px] mx-auto text-center">
    <form class="mb-2">
      <div>
        <input
          class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
          v-model="email"
          type="email"
          placeholder="Электронная почта"
        />
      </div>

      <div>
        <input
          class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
          v-model="password"
          type="password"
          placeholder="пароль"
        />
      </div>

      <div>
        <input
          class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
          v-model="confirmPassword"
          type="password"
          placeholder="Повторить пароль"
        />
      </div>
    </form>

    <div class="flex gap-2 justify-center mb-2">
      <RegisterButton :active="isRegisterActive" />
      <LoginButton :active="isLoginActive" />
    </div>
  </section>
</template>
