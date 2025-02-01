// Работа с API сервером, пока просто заглушки на будущее

import type { Challenge, Room, User } from './types'

// Датасет различных безделушек
// Заглушки на будущее
// после эти данные должны будут загружаться с сервера
//
// users: Пара моделей пользователей для тестов
const users: User[] = [
  {
    id: 'm1',
    name: 'Milinuri',
    avatar:
      'https://yt3.googleusercontent.com/T1ktOCyx03sO3RztTkblKrgmP2AWB9S4MHp4uvJyzJihXDtOJ5112pXDcb--tisSt5Gub6pC=s900-c-k-c0x00ffffff-no-rj',
    gems: 3720,
    playCount: 312,
    winCount: 112,
    cardsCount: 5421,
  },
  {
    id: 'a4',
    name: 'Sakurai Minami',
    avatar:
      'https://static.wikia.nocookie.net/mahouka-koukou-no-rettousei/images/6/6b/MKnR-AN-S2-E11-SC-32.png/revision/latest/scale-to-width-down/1000?cb=20201213001815',
    gems: 4000,
    playCount: 250,
    winCount: 150,
    cardsCount: 5000,
  },
  {
    id: 'a5',
    name: 'Mikasa Ackerman',
    avatar: 'https://i.pinimg.com/736x/54/6a/c2/546ac2b68c23419362ca1fc061733004.jpg',
    gems: 2900,
    playCount: 180,
    winCount: 90,
    cardsCount: 3500,
  },
  {
    id: 'a6',
    name: 'Lura van Renia',
    avatar:
      'https://sun9-54.userapi.com/s/v1/ig2/cBPfLce_F8wGtjct1gePcRHWslyJmVQb62pTMVVB2UGuqco4zIgoXZ2jZ4vP5eIj8iZQYVuZ8OZ9wmSQcu3dWeXY.jpg?quality=95&as=32x32,48x48,72x72,108x108,160x160,240x240,360x360,480x480,540x540,640x640,720x720,1080x1080&from=bu&u=9ybjRauGEXr3jreRhUdYplvX0kY4IEDbB7VnoEJwQZc&cs=807x807',
    gems: 4500,
    playCount: 300,
    winCount: 200,
    cardsCount: 6000,
  },
  {
    id: 'a7',
    name: 'Rumia',
    avatar: 'https://i.pinimg.com/originals/12/00/4e/12004eebeb8bf2868d93bf2565c25da0.jpg',
    gems: 2300,
    playCount: 160,
    winCount: 80,
    cardsCount: 2800,
  },
  {
    id: 'a8',
    name: 'Qq Uwu',
    avatar: 'https://i.pinimg.com/originals/b1/9f/1a/b19f1a99d68179cd1cbcb2e06b27e5ef.jpg',
    gems: 3100,
    playCount: 190,
    winCount: 110,
    cardsCount: 3700,
  },
  {
    id: 'a9',
    name: 'Edward Elric',
    avatar: 'https://i.pinimg.com/736x/5b/23/ee/5b23ee721cfa2139273c601f3e3414fd.jpg',
    gems: 3600,
    playCount: 220,
    winCount: 130,
    cardsCount: 4500,
  },
  {
    id: 'a10',
    name: 'Rem',
    avatar: 'https://i.pinimg.com/736x/20/14/a3/2014a3d972c5488510b1841a876f2e3f.jpg',
    gems: 2800,
    playCount: 140,
    winCount: 70,
    cardsCount: 3200,
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

// методы API для получения данных
// TODO: Пусть тут будет логика работы с сервером наконец

// пользователи --------------------------------------------------------

export function getMyId() {
  return users[0].id
}

export function getMe(): User {
  return users[0]
}

export function getUserById(userId: string): User | undefined {
  for (const user of users) {
    if (user.id == userId) {
      return user
    }
  }
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
  return users.sort((a, b) => b.playCount - a.playCount)
}

export function getTopCards() {
  return users.sort((a, b) => b.cardsCount - a.cardsCount)
}

export function getTopWins() {
  return users.sort((a, b) => b.winCount - a.winCount)
}

export function getUserTopIndex(userid: string, mode: string) {
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
    if (user.id === userid) {
      return index + 1
    }
  }

  return 0
}

// Задания -------------------------------------------------------------

export function getChallenges() {
  return challenges
}
