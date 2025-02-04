// Работа с API сервером, пока просто заглушки на будущее

import { toValue } from 'vue'
import type { Challenge, Room, User, UserDataIn } from './types'

// Датасет различных безделушек
// Заглушки на будущее
// после эти данные должны будут загружаться с сервера
//

const rooms: Room[] = [
  {
    id: 'r0',
    owner: 'milinuri',
    players: ['milinuri'],
    minPlayers: 2,
    maxPlayers: 3,
    gems: 50,
    private: true,
  },
  {
    id: 'r1',
    owner: 'mikasa',
    players: ['mikasa', 'minami'],
    minPlayers: 3,
    maxPlayers: 4,
    gems: 75,
    private: false,
  },
  {
    id: 'r2',
    owner: 'miro',
    players: ['miro', 'milinuri'],
    minPlayers: 2,
    maxPlayers: 2,
    gems: 25,
    private: false,
  },
  {
    id: 'r6',
    owner: 'renilura',
    players: ['renilura', 'remrin', 'qquwu', 'renilura'],
    minPlayers: 4,
    maxPlayers: 7,
    gems: 250,
    private: false,
  },
]

const challenges: Challenge[] = [
  { name: 'Сыграть 5 раз', now: 2, total: 5, reward: 25 },
  { name: 'Разыграть 70 карт', now: 52, total: 70, reward: 80 },
  { name: 'Выбросить пару +2 подряд', now: 2, total: 7, reward: 400 },
]

// Вспомогательные функция для использования API -----------------------

const API_URL = import.meta.env.VITE_API_URL

async function useApi(url: string, req?: RequestInit) {
  const res = await fetch(API_URL + toValue(url), req)

  try {
    if (!res.ok) {
      return { error: true, data: await res.json() }
    }
    return { error: false, data: await res.json() }
  } catch (error) {
    return { error: true, data: error }
  }
}

// методы API для получения данных
// TODO: Пусть тут будет логика работы с сервером наконец

// пользователи --------------------------------------------------------

export async function loginUser(user: UserDataIn) {
  return await useApi('/users/login', {
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
    body: JSON.stringify(user),
  })
}

export async function registerUser(user: UserDataIn) {
  return await useApi('/users/', {
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
    body: JSON.stringify(user),
  })
}

export async function getUser(token: string) {
  return await useApi('/users/me', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  })
}

export async function updateUser(token: string, profile: { name: string; avatar_url: string }) {
  return await useApi('/users/', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    method: 'PUT',
    body: JSON.stringify(profile),
  })
}

export async function changeUserPassword(
  token: string,
  password: { old_password: string; new_password: string },
) {
  return await useApi('/users/change-password', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    method: 'POST',
    body: JSON.stringify(password),
  })
}

export async function getUserById(username: string) {
  return await useApi('/users/' + username, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.error) {
      return null
    }
    return res.data as User
  })
}

// Комнаты -------------------------------------------------------------

export function getRooms() {
  const res = []
  for (const room of rooms) {
    if (!room.private) {
      res.push(room)
    }
  }
  return res
}

export function getRoomById(roomID: string) {
  for (const room of rooms) {
    if (room.id == roomID) {
      return room
    }
  }
}

export function createRoom() {
  return 'r0'
}

export function getRandomRoom() {
  return 'r2'
}

// TODO: Вспомогательная функция, будет убрана после
export async function getPlayersForRooms(rooms: Room[]) {
  const res: [Room, User][] = []
  for (const room of rooms) {
    const owner = await getUserById(room.owner)
    if (!owner) {
      continue
    }
    res.push([room, owner])
  }
  return res
}

// Таблица лидеров -----------------------------------------------------

export type Category = 'gems' | `games` | `wins` | `cards`

export async function getLeaders(category: Category) {
  return await useApi('/leaderboard/' + category, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.error) {
      return null
    }
    return res.data as User[]
  })
}

export async function getLeaderboardIndex(username: string, category: Category) {
  return await useApi(`/leaderboard/${username}/${category}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.error) {
      return null
    }
    return res.data
  })
}

// Задания -------------------------------------------------------------

export function getChallenges() {
  return challenges
}
