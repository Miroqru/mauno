// Работа с API сервером, пока просто заглушки на будущее

import { toValue } from 'vue'
import type { Challenge, Room, User, UserDataIn } from './types'

// Датасет различных безделушек
// Заглушки на будущее
// после эти данные должны будут загружаться с сервера
//
// users: Пара моделей пользователей для тестов
const users: User[] = [
  {
    username: 'milinuri',
    name: 'Milinuri',
    avatar_url:
      'https://yt3.googleusercontent.com/T1ktOCyx03sO3RztTkblKrgmP2AWB9S4MHp4uvJyzJihXDtOJ5112pXDcb--tisSt5Gub6pC=s900-c-k-c0x00ffffff-no-rj',
    gems: 3720,
    play_count: 312,
    win_count: 112,
    cards_count: 5421,
  },
  {
    username: 'minami',
    name: 'Sakurai Minami',
    avatar_url:
      'https://static.wikia.nocookie.net/mahouka-koukou-no-rettousei/images/6/6b/MKnR-AN-S2-E11-SC-32.png/revision/latest/scale-to-width-down/1000?cb=20201213001815',
    gems: 4000,
    play_count: 250,
    win_count: 150,
    cards_count: 5000,
  },
  {
    username: 'mikasa',
    name: 'Mikasa Ackerman',
    avatar_url: 'https://i.pinimg.com/736x/54/6a/c2/546ac2b68c23419362ca1fc061733004.jpg',
    gems: 2900,
    play_count: 180,
    win_count: 90,
    cards_count: 3500,
  },
  {
    username: 'renilura',
    name: 'Lura van Renia',
    avatar_url:
      'https://sun9-54.userapi.com/s/v1/ig2/cBPfLce_F8wGtjct1gePcRHWslyJmVQb62pTMVVB2UGuqco4zIgoXZ2jZ4vP5eIj8iZQYVuZ8OZ9wmSQcu3dWeXY.jpg?quality=95&as=32x32,48x48,72x72,108x108,160x160,240x240,360x360,480x480,540x540,640x640,720x720,1080x1080&from=bu&u=9ybjRauGEXr3jreRhUdYplvX0kY4IEDbB7VnoEJwQZc&cs=807x807',
    gems: 4500,
    play_count: 300,
    win_count: 200,
    cards_count: 6000,
  },
  {
    username: 'rumia',
    name: 'Rumia',
    avatar_url: 'https://i.pinimg.com/originals/12/00/4e/12004eebeb8bf2868d93bf2565c25da0.jpg',
    gems: 2300,
    play_count: 160,
    win_count: 80,
    cards_count: 2800,
  },
  {
    username: 'qquwu',
    name: 'Qq Uwu',
    avatar_url: 'https://i.pinimg.com/originals/b1/9f/1a/b19f1a99d68179cd1cbcb2e06b27e5ef.jpg',
    gems: 3100,
    play_count: 190,
    win_count: 110,
    cards_count: 3700,
  },
  {
    username: 'fullmethallalchemist',
    name: 'Edward Elric',
    avatar_url: 'https://i.pinimg.com/736x/5b/23/ee/5b23ee721cfa2139273c601f3e3414fd.jpg',
    gems: 3600,
    play_count: 220,
    win_count: 130,
    cards_count: 4500,
  },
  {
    username: 'remrin',
    name: 'Rem',
    avatar_url: 'https://i.pinimg.com/736x/20/14/a3/2014a3d972c5488510b1841a876f2e3f.jpg',
    gems: 2800,
    play_count: 140,
    win_count: 70,
    cards_count: 3200,
  },
]

const rooms: Room[] = [
  {
    id: 'r0',
    owner: 'm1',
    players: ['m1'],
    minPlayers: 2,
    maxPlayers: 3,
    gems: 50,
    private: true,
  },
  {
    id: 'r1',
    owner: 'a8',
    players: ['a8', 'a10'],
    minPlayers: 3,
    maxPlayers: 4,
    gems: 75,
    private: false,
  },
  {
    id: 'r2',
    owner: 'a5',
    players: ['a5', 'm1'],
    minPlayers: 2,
    maxPlayers: 2,
    gems: 25,
    private: false,
  },
  {
    id: 'r6',
    owner: 'a6',
    players: ['a8', 'a9', 'a4'],
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
  return await useApi('/users', {
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

export function getUserById(username: string) {
  return useApi('/users/' + username, {
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

// Таблица лидеров -----------------------------------------------------

export function getTopGems() {
  return users.sort((a, b) => b.gems - a.gems)
}

export function getTopGames() {
  return users.sort((a, b) => b.play_count - a.play_count)
}

export function getTopCards() {
  return users.sort((a, b) => b.cards_count - a.cards_count)
}

export function getTopWins() {
  return users.sort((a, b) => b.win_count - a.win_count)
}

export function getUserTopIndex(username: string, mode: string) {
  let leaders = []
  if (mode == 'gems') {
    leaders = getTopGems()
  } else if (mode == 'games') {
    leaders = getTopGames()
  } else if (mode == 'wind') {
    leaders = getTopWins()
  } else {
    leaders = getTopCards()
  }

  for (const [index, user] of leaders.entries()) {
    if (user.username === username) {
      return index + 1
    }
  }

  return 0
}

// Задания -------------------------------------------------------------

export function getChallenges() {
  return challenges
}
