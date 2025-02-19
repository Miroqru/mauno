import type { Card, EditUserDataIn, Room, RoomDataIn, RoomFilter, User } from './types'
import { useRouter } from 'vue-router'
import { useNotifyStore } from '../stores/notify'
import { useUserStore } from '../stores/user'
import * as method from './api'

// Инициализация хранилищ
const userState = useUserStore()
const notifyState = useNotifyStore()
const router = useRouter()

// Пользователь ----------------------------------------------------------------

export async function updateUser(user: EditUserDataIn): Promise<User | null> {
  const res = await method.updateUser(userState.userToken as string, user)
  if (res.type === 'left') {
    notifyState.addNotify('Пользователь', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function updateUserPassword(password: { old_password: string, new_password: string },
): Promise<User | null> {
  const res = await method.changeUserPassword(userState.userToken as string, password)
  if (res.type === 'left') {
    notifyState.addNotify('Пользователь', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function getUser(username: string): Promise<User | null> {
  const res = await method.fetchUserById(username)
  if (res.type === 'left') {
    notifyState.addNotify('Пользователи', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

// Комнаты ---------------------------------------------------------------------

export async function getRooms(filter?: RoomFilter): Promise<Room[]> {
  const res = await method.fetchRooms(filter)
  if (res.type === 'left') {
    notifyState.addNotify('Комнаты', res.value, 'error')
    return []
  }
  else {
    return res.value
  }
}

export async function getRoom(roomID: string): Promise<Room | null> {
  const res = await method.fetchRoomById(roomID)
  if (res.type === 'left') {
    notifyState.addNotify('Комната', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function updateRoom(roomID: string, roomData: RoomDataIn): Promise<Room | null> {
  const res = await method.updateRoom(roomID, userState.userToken as string, roomData)
  if (res.type === 'left') {
    notifyState.addNotify('Настройки', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

// В отличие от прочих это действие без результата
export async function newRoom() {
  const res = await method.createRoom(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Новая комната', res.value, 'error')
  }
  else {
    await router.push(`/room/${res.value.id}`)
  }
}

export async function randomRoom() {
  const res = await method.fetchRandomRoom()
  if (res.type === 'left') {
    notifyState.addNotify('Случайная комната', res.value, 'error')
  }
  else {
    await router.push(`/room/${res.value.id}`)
  }
}

export async function kickRoomUser(roomID: string, userID: string) {
  const res = await method.kickUserFromRoom(userState.userToken as string, roomID, userID)
  if (res.type === 'left') {
    notifyState.addNotify('исключение', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function setRoomOwner(roomID: string, userID: string) {
  const res = await method.setOwnerInRoom(userState.userToken as string, roomID, userID)
  if (res.type === 'left') {
    notifyState.addNotify('Владелец', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function getRoomRules(roomID: string) {
  const res = await method.fetchRoomRules(roomID)
  if (res.type === 'left') {
    notifyState.addNotify('Правила', res.value, 'error')
    return []
  }
  else {
    return res.value
  }
}

export async function setRoomRules(roomID: string, rules: string[]) {
  const res = await method.updateRoomRules(roomID, userState.userToken as string, rules)
  if (res.type === 'left') {
    notifyState.addNotify('Правила', res.value, 'error')
    return []
  }
  else {
    return res.value
  }
}

// Таблица лидеров  ------------------------------------------------------------

export async function getRating(category: method.Category) {
  const res = await method.fetchLeaders(category)
  if (res.type === 'left') {
    notifyState.addNotify('Таблица лидеров', res.value, 'error')
    return []
  }
  else {
    return res.value
  }
}

export async function getRatingIndex(username: string, category: method.Category) {
  const res = await method.fetchLeaderboardIndex(username, category)
  if (res.type === 'left') {
    notifyState.addNotify('Таблица лидеров', res.value, 'error')
    return 0
  }
  else {
    return res.value
  }
}

// игра ------------------------------------------------------------------------

export async function joinGame() {
  const res = await method.joinGame(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Игра', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function leaveGame() {
  const res = await method.leaveGame(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Выход из игры', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

// Сессия
export async function getGame() {
  const res = await method.fetchGame(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Игра', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function startGame() {
  const res = await method.startGame(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Новая игра', res.value, 'error')
  }
  else {
    await router.push('/game/')
  }
}

export async function endGame() {
  const res = await method.endGame(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Завершение игры', res.value, 'error')
  }
  else {
    await router.push('/home/')
  }
}

export async function kickPlayer(player: string) {
  const res = await method.kickPlayer(userState.userToken as string, player)
  if (res.type === 'left') {
    notifyState.addNotify('Изгнание', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function skipPlayer() {
  const res = await method.skipPlayer(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Пропуск игрока', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

// Ход игрока
export async function nextTurn() {
  const res = await method.nextTurn(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Игра', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function takeCards() {
  const res = await method.takeCards(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Взятие карт', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function shotgunTake() {
  const res = await method.shotgunTake(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Взятие карт', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function shotgunShot() {
  const res = await method.shotgunShot(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Выстрел', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function bluffCard() {
  const res = await method.bluffCard(userState.userToken as string)
  if (res.type === 'left') {
    notifyState.addNotify('Проверка на честность', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function selectColor(color: number) {
  const res = await method.selectColor(userState.userToken as string, color)
  if (res.type === 'left') {
    notifyState.addNotify('Выбор цвета', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function selectPlayer(player: string) {
  const res = await method.selectPlayer(userState.userToken as string, player)
  if (res.type === 'left') {
    notifyState.addNotify('Выбор игрока', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}

export async function pushCard(card: Card) {
  const res = await method.pushCard(userState.userToken as string, card)
  if (res.type === 'left') {
    notifyState.addNotify('Отправка карты', res.value, 'error')
    return null
  }
  else {
    return res.value
  }
}
