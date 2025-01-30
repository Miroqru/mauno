// Работа с API сервером, пока просто заглушки на будущее

import type { User } from './types'

function getMe(): User {
  return {
    name: 'Milinuri',
    avatar: 'https://placewaifu.com/image/200',
    gems: 3720,
    playCount: 312,
    winCount: 112,
    cardsCount: 5421,
  }
}
