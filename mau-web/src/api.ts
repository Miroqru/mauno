// Работа с API сервером, пока просто заглушки на будущее

import type { User } from './types'

export function getMe(): User {
  return {
    name: 'Milinuri',
    avatar: 'https://yt3.googleusercontent.com/T1ktOCyx03sO3RztTkblKrgmP2AWB9S4MHp4uvJyzJihXDtOJ5112pXDcb--tisSt5Gub6pC=s900-c-k-c0x00ffffff-no-rj',
    gems: 3720,
    playCount: 312,
    winCount: 112,
    cardsCount: 5421,
  }
}
