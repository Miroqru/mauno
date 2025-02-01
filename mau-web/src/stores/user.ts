import { getUserById } from '@/api'
import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userId: Ref<string | null, string | null> = ref(localStorage.getItem('userId'))
  const userToken: Ref<string | null, string | null> = ref(localStorage.getItem('userToken'))

  function logIn(id: string, token: string) {
    localStorage.setItem('userId', id)
    localStorage.setItem('userToken', token)
    userId.value = id
    userToken.value = token
  }

  function logOut() {
    localStorage.removeItem('userId')
    localStorage.removeItem('userToken')
    userId.value = null
    userToken.value = null
  }

  function getMe() {
    if (!userId.value) {
      return null
    }
    const userData = getUserById(userId.value)
    if (!userData) {
      logOut()
    }
    return userData
  }

  return { userId, userToken, logIn, logOut, getMe }
})
