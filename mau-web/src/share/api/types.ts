// Общие типы, используемые на сайте

// Данные пользователя для регистрации / входа
export interface UserDataIn {
  username: string
  password: string
}

export interface EditUserDataIn { name: string, avatar_url: string }

// Данные комнаты, которые можно изменить
export interface RoomDataIn {
  name: string
  private: boolean
  room_password: string
  gems: number
  max_players: number
  min_players: number
}

export type RoomOrder = 'create_time' | 'gems' | 'players'
export type RoomStatus = 'idle' | 'game' | 'ended'

export interface RoomFilter {
  reverse: boolean
  orderBy: RoomOrder
}

export interface RoomRuleData {
  key: string
  name: string
  status: boolean
}

// username - Уникальное имя пользователя
// name - Отображаемое имя пользователя
// avatar - ссылка на аватар
// gem - количество кристаллов
// play_count - сколько сыграно игр всего
// win_count- сколько было побед
// card_count - сколько карт разыграно
export interface User {
  username: string
  name: string
  avatar_url: string
  gems: number
  play_count: number
  win_count: number
  cards_count: number
}

// комнатки, в которых собираются игроки уно
//
// id - уникальный id комнаты
// owner - кто является владельцем комнаты
// players - кто уже подключился к комнате
// minPlayers - сколько нужно игроков для игры
// maxPlayers - максимальное число игроков в комнате
// gems - сколько гемов нужно заплатить за вход
// private - является ли комнатка приватной
export interface Room {
  id: string
  name: string
  create_time: string
  private: boolean
  room_password: string
  owner: User
  players: User[]
  min_players: number
  max_players: number
  gems: number
  status: RoomStatus
  status_updates: string
}

// Игровые задания, за которые можно получить награду
//
// name - краткое название задания
// now - сколько уже выполнено
// total - сколько необходимо сделать
// reward - сколько будет гемов по завершению работы

export interface Challenge {
  name: string
  now: number
  total: number
  reward: number
}
