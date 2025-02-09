import type { User } from '@/types'
import type { Ref } from 'vue'
import { fetchActiveRoom, getRoomById, getUser, joinToRoom, leaveFromRoom } from '@/api'
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

    getUser(userToken.value).then((res) => {
      if (res.type === 'right') {
        user.value = res.value
      }
    })

    return user
  }

  async function joinRoom(room: string) {
    const res = await joinToRoom(userToken.value as string, room)
    if (res.type === 'right') {
      localStorage.setItem('roomId', room)
      roomId.value = room
    }
  }

  async function leaveRoom(room: string) {
    await leaveFromRoom(userToken.value as string, room)
    localStorage.removeItem('roomId')
    roomId.value = null
  }

  function getRoom() {
    const room = ref(null)
    const roomId = getActiveRoom()
    if (roomId.value === null) {
      return room
    }

    getRoomById(roomId.value).then((res) => {
      if (res.type === 'left' || res.value.status === 'ended') {
        localStorage.removeItem('roomId')
        roomId.value = null
      }
      room.value = res.value
    })

    return room
  }

  function getActiveRoom() {
    const activeRoomID = ref(roomId.value)

    if (activeRoomID.value === null) {
      fetchActiveRoom(userToken.value as string).then((res) => {
        if (res.type === 'right') {
          activeRoomID.value = res.value.id
          roomId.value = res.value.id
          localStorage.setItem('roomId', res.value.id)
        }
      })
    }

    return activeRoomID
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
    getActiveRoom,
  }
})
