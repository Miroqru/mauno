import { getRoomById, getUser } from '@/api'
import type { User } from '@/types'
import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userId: Ref<string | null, string | null> = ref(localStorage.getItem('userId'))
  const userToken: Ref<string | null, string | null> = ref(localStorage.getItem('userToken'))
  const roomId: Ref<string | null, string | null> = ref(localStorage.getItem('roomId'))

  function logIn(username: string, token: string) {
    localStorage.setItem('userId', username)
    localStorage.setItem('userToken', token)
    userId.value = username
    userToken.value = token
  }

  function logOut() {
    localStorage.removeItem('userId')
    localStorage.removeItem('userToken')
    userId.value = null
    userToken.value = null
    leaveRoom()
  }

  function getMe() {
    const user: Ref<User | null, User | null> = ref(null)
    if (!userToken.value) {
      return user
    }

    getUser(userToken.value).then(({ data }) => {
      user.value = data
    })

    return user
  }

  function joinRoom(room: string) {
    localStorage.setItem('roomId', room)
    roomId.value = room
  }

  function leaveRoom() {
    localStorage.removeItem('roomId')
    roomId.value = null
  }

  function getRoom() {
    if (!roomId.value) {
      return null
    }
    const room = getRoomById(roomId.value)
    console.log(room)
    if (!room) {
      leaveRoom()
      return null
    }
    return room
  }

  return {
    userId,
    userToken,
    roomId,
    logIn,
    logOut,
    getMe,
    joinRoom,
    leaveRoom,
    getRoom,
  }
})
