import { getRoomById, getUserById } from '@/api'
import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userId: Ref<string | null, string | null> = ref(localStorage.getItem('userId'))
  const userToken: Ref<string | null, string | null> = ref(localStorage.getItem('userToken'))
  const roomId: Ref<string | null, string | null> = ref(localStorage.getItem('roomId'))

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
    leaveRoom()
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
