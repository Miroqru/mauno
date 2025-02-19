import type { Either } from '@/share/api/either'
import type {
  Card,
  Category,
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
import { useUserStore } from '../stores/user'

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
const userState = useUserStore()

async function useApi(url: string, req?: RequestInit): Promise<Either<any, any>> {
  const res = await fetch(API_URL + toValue(url), {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${userState.userToken}`,
    },

    ...req,
  })

  try {
    if (!res.ok) {
      return left(await res.json())
    }
    return right(await res.json())
  } catch (error) {
    return left(error)
  }
}

interface LoginApiResult {
  ok: boolean
  token: string
}

type ApiResponse<T> = Promise<Either<any, T>>
type GameResponse = ApiResponse<GameContext>

export default {
  async loginUser(user: UserDataIn): ApiResponse<LoginApiResult> {
    return await useApi('/users/login', {
      method: 'POST',
      body: JSON.stringify(user),
    })
  },

  async registerUser(user: UserDataIn): ApiResponse<{ status: boolean; token: string }> {
    return await useApi('/users/', {
      method: 'POST',
      body: JSON.stringify(user),
    })
  },

  async fetchUser(): ApiResponse<User> {
    return await useApi('/users/me')
  },

  async updateUser(profile: EditUserDataIn): ApiResponse<User> {
    return await useApi('/users/', {
      method: 'PUT',
      body: JSON.stringify(profile),
    })
  },

  async changeUserPassword(password: {
    old_password: string
    new_password: string
  }): ApiResponse<User> {
    return await useApi('/users/change-password', {
      method: 'POST',
      body: JSON.stringify(password),
    })
  },

  async fetchUserById(username: string): ApiResponse<User> {
    return await useApi(`/users/${username}`)
  },

  // Комнаты -------------------------------------------------------------

  async fetchRooms(filter?: RoomFilter): ApiResponse<Room[]> {
    return await useApi(
      filter !== undefined
        ? `/rooms/?order_by=${filter.orderBy}&invert=${filter.reverse}`
        : '/rooms/',
    )
  },

  async fetchRoomById(roomID: string): ApiResponse<Room> {
    return await useApi(`/rooms/${roomID}`)
  },

  async updateRoom(roomID: string, roomData: RoomDataIn): ApiResponse<Room> {
    return await useApi(`/rooms/${roomID}`, {
      method: 'PUT',
      body: JSON.stringify(roomData),
    })
  },

  async createRoom(): ApiResponse<Room> {
    return await useApi('/rooms/', { method: 'POST' })
  },

  async fetchRandomRoom(): Promise<Either<any, Room>> {
    return await useApi('/rooms/random')
  },

  async fetchActiveRoom(): Promise<Either<any, Room>> {
    return await useApi('/rooms/active')
  },

  async joinToRoom(roomID: string): Promise<Either<any, Room>> {
    return await useApi(`/rooms/${roomID}/join/`, { method: 'POST' })
  },

  async leaveFromRoom(roomID: string): Promise<Either<any, Room>> {
    return await useApi(`/rooms/${roomID}/leave/`, { method: 'POST' })
  },

  async kickUserFromRoom(roomID: string, userID: string): Promise<Either<any, Room>> {
    return await useApi(`/rooms/${roomID}/kick/${userID}`, { method: 'POST' })
  },

  async setOwnerInRoom(roomID: string, userID: string): ApiResponse<Room> {
    return await useApi(`/rooms/${roomID}/owner/${userID}`, { method: 'POST' })
  },

  async fetchRoomRules(roomID: string): ApiResponse<RoomRuleData[]> {
    return await useApi(`/rooms/${roomID}/modes/`)
  },

  async updateRoomRules(roomID: string, rules: string[]): ApiResponse<RoomRuleData[]> {
    return await useApi(`/rooms/${roomID}/modes`, {
      method: 'PUT',
      body: JSON.stringify({ rules }),
    })
  },

  // Таблица лидеров -----------------------------------------------------

  async fetchLeaders(category: Category): ApiResponse<User[]> {
    return await useApi(`/leaderboard/${category}`)
  },

  async fetchLeaderboardIndex(username: string, category: Category): ApiResponse<number> {
    return await useApi(`/leaderboard/${username}/${category}`)
  },

  // Задания -------------------------------------------------------------------

  getChallenges() {
    return challenges
  },

  // Игровая сессия ------------------------------------------------------------

  // Игрок
  async joinGame(): GameResponse {
    return await useApi('/game/join', { method: 'post' })
  },

  async leaveGame(): GameResponse {
    return await useApi('/game/leave', { method: 'post' })
  },

  // Сессия
  async fetchGame(): GameResponse {
    return await useApi('/game/')
  },

  async startGame(): GameResponse {
    return await useApi('/game/start', { method: 'post' })
  },

  async endGame(): GameResponse {
    return await useApi('/game/end', { method: 'post' })
  },

  async kickPlayer(player: string): GameResponse {
    return await useApi(`/game/kick/${player}`, { method: 'post' })
  },

  async skipPlayer(): GameResponse {
    return await useApi('/game/skip', { method: 'post' })
  },

  // Ход
  async nextTurn(): GameResponse {
    return await useApi('/game/next', { method: 'post' })
  },

  async takeCards(): GameResponse {
    return await useApi('/game/take', { method: 'post' })
  },

  async shotgunTake(): GameResponse {
    return await useApi('/game/shotgun/take', { method: 'post' })
  },

  async shotgunShot(): GameResponse {
    return await useApi('/game/shotgun/shot', { method: 'post' })
  },

  async bluffCard(): GameResponse {
    return await useApi('/game/bluff', { method: 'post' })
  },

  async selectColor(color: number): GameResponse {
    return await useApi(`/game/color/${color}`, { method: 'post' })
  },

  async selectPlayer(player: string): GameResponse {
    return await useApi(`/game/player/${player}`, { method: 'post' })
  },

  async pushCard(card: Card): GameResponse {
    return await useApi(`/game/card`, {
      method: 'post',
      body: JSON.stringify(card),
    })
  },
}
