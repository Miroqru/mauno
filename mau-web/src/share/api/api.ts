// Работа с API сервером, пока просто заглушки на будущее

import type { Either } from '@/share/api/either'
import type {
  Challenge,
  EditUserDataIn,
  GameContext,
  Room,
  RoomDataIn,
  RoomFilter,
  RoomRuleData,
  User,
  UserDataIn,
} from '@/share/api/types'
import { left, right } from '@/share/api/either'
import { toValue } from 'vue'

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

export async function fetchUser(token: string): Promise<Either<any, User>> {
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

export async function fetchUserById(username: string): Promise<Either<null, User>> {
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

export async function fetchRooms(filter?: RoomFilter): Promise<Either<any, Room[]>> {
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

export async function fetchRoomById(roomID: string): Promise<Either<any, Room>> {
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

export async function fetchRandomRoom(): Promise<Either<any, Room>> {
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

export async function fetchRoomRules(roomID: string): Promise<Either<any, RoomRuleData[]>> {
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

export async function fetchLeaders(category: Category): Promise<Either<null, User[]>> {
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

export async function fetchLeaderboardIndex(
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

// Игра ----------------------------------------------------------------

// Игрок
export async function joinGame(token: string): Promise<Either<any, GameContext>> {
  return await useApi('/game/join', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function leaveGame(token: string): Promise<Either<any, GameContext>> {
  return await useApi('/game/leave', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

// Сессия
export async function fetchGame(token: string): Promise<Either<any, GameContext>> {
  return await useApi('/game/', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function startGame(token: string): Promise<Either<any, any>> {
  return await useApi('/game/start', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function endGame(token: string): Promise<Either<any, any>> {
  return await useApi('/game/end', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function kickPlayer(token: string, player: string): Promise<Either<any, any>> {
  return await useApi(`/game/kick/${player}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function skipPlayer(token: string): Promise<Either<any, any>> {
  return await useApi('/game/skip', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

// Ход
export async function nextTurn(token: string): Promise<Either<any, any>> {
  return await useApi('/game/next', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function takeCards(token: string): Promise<Either<any, any>> {
  return await useApi('/game/take', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function shotgunTake(token: string): Promise<Either<any, any>> {
  return await useApi('/game/shotgun/take', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function shotgunShot(token: string): Promise<Either<any, any>> {
  return await useApi('/game/shotgun/shot', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function bluffCard(token: string): Promise<Either<any, any>> {
  return await useApi('/game/bluff', {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function selectColor(token: string, color: number): Promise<Either<any, any>> {
  return await useApi(`/game/color/${color}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function selectPlayer(token: string, player: number): Promise<Either<any, any>> {
  return await useApi(`/game/player/${player}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}

export async function pushCard(token: string, card: string): Promise<Either<any, any>> {
  return await useApi(`/game/card/${card}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
}
