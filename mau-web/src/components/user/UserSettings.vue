<script setup lang="ts">
import type { User } from '@/share/api/types'
import { updateUser, updateUserPassword } from '@/share/api'
import { useUserStore } from '@/share/stores/user'
import { Check } from 'lucide-vue-next'
import { computed, ref } from 'vue'

const { user } = defineProps<{ user: User }>()
const userStore = useUserStore()

const name = ref('')
const avatar = ref('')

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const isChangeActive = computed(() => {
  return (
    oldPassword.value !== ''
    && newPassword.value !== ''
    && confirmPassword.value !== ''
    && newPassword.value === confirmPassword.value
  )
})

async function updateProfile() {
  await updateUser({
    name: name.value,
    avatar_url: avatar.value,
  })

  name.value = ''
  avatar.value = ''
}

async function changePassword() {
  await updateUserPassword({
    old_password: oldPassword.value,
    new_password: newPassword.value,
  })

  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
}

// TODO: Раздробить на множество компонентов
</script>

<template>
  <section
    v-if="user.username === userStore.userId"
    class="p-2 border-2 border-stone-700 rounded-md my-4"
  >
    <h2 class="text-lg font-bold mb-2">
      Настройки пользователя
    </h2>

    <div>
      <input
        v-model="name"
        class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
        type="text"
        :placeholder="`Имя пользователя (${user.name})`"
      >
    </div>

    <div>
      <input
        v-model="avatar"
        class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
        type="text"
        placeholder="Ссылка на аватар"
      >
    </div>
    <button
      class="bg-stone-700 hover:bg-stone-600 transition flex gap-2 p-1 rounded-md"
      @click="updateProfile"
    >
      <Check />
      <div>Обновить</div>
    </button>

    <h2 class="text-lg font-bold mb-2">
      Смена пароля
    </h2>
    <div>
      <input
        v-model="oldPassword"
        class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
        type="password"
        placeholder="Текущий пароль"
      >
    </div>

    <div>
      <input
        v-model="newPassword"
        class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
        type="password"
        placeholder="Новый пароль"
      >
    </div>

    <div>
      <input
        v-model="confirmPassword"
        class="invalid:border-pink-500 invalid:text-pink-600 focus:border-teal-500 focus:outline focus:outline-teal-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 p-2 m-2 bg-stone-800 border-2 border-stone-700 transition rounded-md"
        type="password"
        placeholder="Повтор пароля"
      >
    </div>

    <button
      v-if="isChangeActive"
      class="bg-stone-700 hover:bg-stone-600 transition flex gap-2 p-1 rounded-md"
      @click="changePassword"
    >
      <Check />
      <div>Обновить</div>
    </button>
  </section>
</template>
