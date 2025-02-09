// Работа с API сервером, пока просто заглушки на будущее

import type { Either } from './either'
import type {
  Challenge,
  EditUserDataIn,
  Room,
  RoomDataIn,
  RoomFilter,
  RoomRuleData,
  User,
  UserDataIn,
} from './types'
import { toValue } from 'vue'
import { left, right } from './either'

// Датасет различных безделушек
// Заглушки на будущее
// после эти данные должны будут загружаться с сервера
//

const challenges: Challenge[] = [
  { name: 'Сыграть 5 раз', now: 2, total: 5, reward: 25 },
  { name: 'Разыграть 70 карт', now: 52, total: 70, reward: 80 },
  { name: 'Выбросить пару +2 подряд', now: 2, total: 7, reward: 400 },
]

// Вспомогательные функция для использования API -----------------------

const API_URL = import.meta.env.VITE_API_URL

async function useApi(url: string, req?: RequestInit): Promise<Either<any, any>> {
  const res = await fetch(API_URL + toValue(url), req)

  try {
    if (!res.ok) {
      return left(await res.json())
    }
    return right(await res.json())
  }
  catch (error) {
    return left(error)
  }
}

// методы API для получения данных

// пользователи --------------------------------------------------------

interface LoginApiResult {
  ok: boolean
  token: string
}

export async function loginUser(user: UserDataIn): Promise<Either<any, LoginApiResult>> {
  return await useApi('/users/login', {
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
    body: JSON.stringify(user),
  })
}

export async function registerUser(
  user: UserDataIn,
): Promise<Either<any, { status: boolean, token: string }>> {
  return await useApi('/users/', {
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
    body: JSON.stringify(user),
  })
}

export async function getUser(token: string): Promise<Either<any, User>> {
  return await useApi('/users/me', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function updateUser(token: string, profile: EditUserDataIn) {
  return await useApi('/users/', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'PUT',
    body: JSON.stringify(profile),
  })
}

export async function changeUserPassword(
  token: string,
  password: { old_password: string, new_password: string },
): Promise<Either<any, User>> {
  return await useApi('/users/change-password', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'POST',
    body: JSON.stringify(password),
  })
}

export async function getUserById(username: string): Promise<Either<null, User>> {
  return await useApi(`/users/${username}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.type === 'left') {
      return left(null)
    }
    return right(res.value as User)
  })
}

// Комнаты -------------------------------------------------------------

export async function getRooms(filter?: RoomFilter): Promise<Either<any, Room[]>> {
  return await useApi(
    filter !== undefined
      ? `/rooms/?order_by=${filter.orderBy}&invert=${filter.reverse}`
      : '/rooms/',
    {
      headers: {
        'Content-Type': 'application/json',
      },
    },
  )
}

export async function getRoomById(roomID: string): Promise<Either<any, Room>> {
  return await useApi(`/rooms/${roomID}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function updateRoom(
  roomID: string,
  token: string,
  roomData: RoomDataIn,
): Promise<Either<any, Room>> {
  return await useApi(`/rooms/${roomID}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'PUT',
    body: JSON.stringify(roomData),
  })
}

export async function createRoom(token: string): Promise<Either<any, Room>> {
  return await useApi('/rooms/', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'POST',
  })
}

export async function getRandomRoom(): Promise<Either<any, Room>> {
  return await useApi('/rooms/random', {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function fetchActiveRoom(token: string): Promise<Either<any, Room>> {
  return await useApi('/rooms/active', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function joinToRoom(token: string, roomID: string): Promise<Either<any, Room>> {
  return await useApi(`/rooms/${roomID}/join/`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'POST',
  })
}

export async function leaveFromRoom(token: string, roomID: string): Promise<Either<any, Room>> {
  return await useApi(`/rooms/${roomID}/leave/`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'POST',
  })
}

export async function kickUserFromRoom(
  token: string,
  roomID: string,
  userID: string,
): Promise<Either<any, Room>> {
  return await useApi(`/rooms/${roomID}/kick/${userID}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'POST',
  })
}

export async function setOwnerInRoom(
  token: string,
  roomID: string,
  userID: string,
): Promise<Either<any, Room>> {
  return await useApi(`/rooms/${roomID}/owner/${userID}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'POST',
  })
}

export async function getRoomModes(roomID: string): Promise<Either<any, RoomRuleData[]>> {
  return await useApi(`/rooms/${roomID}/modes/`, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function updateRoomRules(
  roomID: string,
  token: string,
  rules: string[],
): Promise<Either<any, RoomRuleData[]>> {
  return await useApi(`/rooms/${roomID}/modes`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    method: 'PUT',
    body: JSON.stringify({ rules }),
  })
}

// Таблица лидеров -----------------------------------------------------

export type Category = 'gems' | `games` | `wins` | `cards`

export async function getLeaders(category: Category): Promise<Either<null, User[]>> {
  return await useApi(`/leaderboard/${category}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.type === 'left') {
      return left(null)
    }
    return right(res.value as User[])
  })
}

export async function getLeaderboardIndex(
  username: string,
  category: Category,
): Promise<Either<null, number>> {
  return await useApi(`/leaderboard/${username}/${category}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.type === 'left') {
      return left(null)
    }
    return right(res.value as number)
  })
}

// Задания -------------------------------------------------------------

export function getChallenges() {
  return challenges
}
