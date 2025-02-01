// Общие типы, используемые на сайте

// id - Уникальный строковый id пользователя
// name - имя пользователя
// avatar - ссылка на аватар
// gem - количество кристаллов
// playCount - сколько сыграно игр всего
// winCount - сколько было побед
// cardCount - сколько карт разыграно
export interface User {
  id: string
  name: string
  avatar: string
  gems: number
  playCount: number
  winCount: number
  cardsCount: number
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
  owner: string
  players: string[]
  minPlayers: number
  maxPlayers: number
  gems: number
  private: boolean
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
