// Общие типы, используемые на сайте

// Данные пользователя для регистрации / входа
export interface UserDataIn {
  username: string
  password: string
}

export interface EditUserDataIn {
  name: string
  avatar_url: string
}

// Данные пользователя
// username - Уникальное имя пользователя
// name - Отображаемое имя пользователя
// avatar_ulr - ссылка на аватар
// gems - количество кристаллов
// play_count - сколько сыграно игр всего
// win_count- сколько было побед
// card_count - сколько карт разыграно
//
// Комнаты
// rooms: История комнат пользователя
// my_rooms: История созданных пользователем комнат
//
// Игры
// my_games: Созданные пользователем игры
// win_games: в каких играх победил
// lose_games: в каких играх проиграл
export interface User {
  username: string
  name: string
  avatar_url: string
  gems: number
  play_count: number
  win_count: number
  cards_count: number

  // Комнаты
  rooms: Room[]
  my_rooms: Room[]

  // Игры
  my_games: Game[]
  win_games: Game[]
  lose_games: Game[]
}

// Комнаты -------------------------------------------------------------

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

export interface RoomFilter {
  reverse: boolean
  orderBy: RoomOrder
}

export interface RoomRuleData {
  key: string
  name: string
  status: boolean
}

// В каком состоянии может быть комната
export type RoomStatus = 'idle' | 'game' | 'ended'
export type Category = 'gems' | `games` | `wins` | `cards`

// комнатки, в которых собираются игроки уно
//
// id - уникальный id комнаты
// name - Имя комнаты
// create_time - Когда комната была создана
// private - является ли комнатка приватной
// room_password - пароль для входа в комнату
// owner - кто является владельцем комнаты
// players - кто уже подключился к комнате
// min_players - сколько нужно игроков для игры
// max_players - максимальное число игроков в комнате
// gems - сколько гемов нужно заплатить за вход
// status - В каком состоянии сейчас комната
// status_updated - когда был обновлён статус комнаты
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
  games: Game[]
}

// игры ----------------------------------------------------------------

// Игра
// id: Уникальный идентификатор игры
// create_time: Когда была создана
// end_time: Когда завершилась игра
// owner: владелец игры
// room: в какой комнате происходило
// winners: список победителей
// losers: список проигравших

export interface Game {
  id: string
  create_time: string
  end_time: string
  owner: User
  room: Room
  winners: User[]
  losers: User[]
}

// Доступные цвета карты
export enum CardColor {
  RED = 0,
  YELLOW = 1,
  GREEN = 2,
  BLUE = 3,
  BLACK = 4,
}

// Доступные типы карт
export enum CardType {
  NUMBER = 0,
  TURN = 1,
  REVERSE = 2,
  TAKE = 3,
  CHOOSE_COLOR = 4,
  TAKE_FOUR = 5,
}

// Игровая карта
// color: Цвет карты от 0 до 4.
// card_type: Тип карты, число или активная карта
// value: number
// cost: number
export interface Card {
  color: CardColor
  card_type: CardType
  value: number
  cost: number
}

// Колода карт
// cards: сколько карт ещё доступно
// used: Сколько карт было использовано
export interface Deck {
  top: Card
  cards: number
  used: null
}

// Данные пользователя
// user_id: уникальный идентификатор
// hand: Сколько карт осталось в руке
// shotgun_current: Сколько раз стрелял из револьвера
export interface OtherPlayer {
  user_id: string
  name: string
  hand: number
  shotgun_current: number
}

export interface SortedCards {
  cover: Card[]
  uncover: Card[]
}

// Данные вашего пользователя
// user_id: уникальный идентификатор
// hand: список ваших карт
// shotgun_current: Сколько раз стрелял из револьвера
export interface Player {
  user_id: string
  hand: SortedCards
  shotgun_current: number
}

export enum GameState {
  NEXT = 0,
  CHOOSE_COLOR = 1,
  TWIST_HAND = 2,
  SHOTGUN = 3,
  CONTINUE = 4,
}

// Активная игровая комната
//
// Основная информация
// room_id: К какой комнате привязана игра
// rules: список активных правил
// owner_id: кто владелец комнаты
// game_started: Когда началась игра
// turn_started: когда начался ход
//
// Игрока комнаты
// players: Список оставшихся игроков
// winners: кто успел победить
// losers: Кто проиграл
// current_player: Кто сейчас ходит. индекс игрока
//
// Состояние комнаты
// deck: Статистика о колоде карт
// reverse: Развёрнут ли порядок ходов
// bluff_flag: Блефует ли то-то
// take_flag: Берёт ли кто-то
// take_counter: счётчик карт для взятия
// shotgun_current: Сколько раз стреляли из револьвера
export interface ActiveGame {
  // Основная информация
  room_id: string
  rules: RoomRuleData[]
  owner_id: string
  game_started: string
  turn_started: string

  // Игрока комнаты
  players: OtherPlayer[]
  winners: OtherPlayer[]
  losers: OtherPlayer[]
  current_player: number

  // Состояние комнаты
  deck: Deck
  reverse: boolean
  take_flag: boolean
  take_counter: number
  shotgun_current: number
  state: GameState
}

// Игровой контекст
// game: Текущая игра
// player: текущий игрок
export interface GameContext {
  game: ActiveGame | null
  player: Player | null
}

// испытания -----------------------------------------------------------

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
