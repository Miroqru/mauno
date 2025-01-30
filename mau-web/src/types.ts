// Общие типы, используемые на сайте

// name - имя пользователя
// avatar - ссылка на аватар
// gem - количество кристаллов
// playCount - сколько сыграно игр всего
// winCount - сколько было побед
// cardCount - сколько карт разыграно
export interface User {
  name: string
  avatar: string
  gems: number
  playCount: number
  winCount: number
  cardsCount: number
}
