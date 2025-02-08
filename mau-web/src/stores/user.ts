import type { User } from '@/types'
import type { Ref } from 'vue'
import { getRoomById, getUser, joinToRoom, leaveFromRoom } from '@/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userId: Ref<string | null> = ref(localStorage.getItem('userId'))
  const userToken: Ref<string | null> = ref(localStorage.getItem('userToken'))
  const roomId: Ref<string | null> = ref(localStorage.getItem('roomId'))

  function logIn(username: string, token: string) {
    localStorage.setItem('userId', username)
    localStorage.setItem('userToken', token)
    userId.value = username
    userToken.value = token
  }

  function logOut() {
    if (roomId.value) {
      leaveRoom(roomId.value)
    }
    localStorage.removeItem('userId')
    localStorage.removeItem('userToken')
    localStorage.removeItem('roomID')
    userId.value = null
    userToken.value = null
    roomId.value = null
  }

  function getMe() {
    const user: Ref<User | null> = ref(null)
    if (!userToken.value) {
      return user
    }

    getUser(userToken.value).then(({ data }) => {
      user.value = data
    })

    return user
  }

  async function joinRoom(room: string) {
    const res = await joinToRoom(userToken.value as string, room)
    if (!res.error) {
      localStorage.setItem('roomId', room)
      roomId.value = room
    }
  }

  async function leaveRoom(room: string) {
    const res = await leaveFromRoom(userToken.value as string, room)
    if (!res.error) {
      localStorage.removeItem('roomId')
      roomId.value = null
    }
  }

  function getRoom() {
    const room = ref(null)
    if (!roomId.value) {
      return room
    }

    getRoomById(roomId.value).then((res) => {
      if (res.error || res.data.status === 'ended') {
        localStorage.removeItem('roomId')
        roomId.value = null
      }
      room.value = res.data
    })

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
