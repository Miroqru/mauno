import MainVew from '@/views/MainVew.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'lending',
      component: MainVew,
    },
    {
      path: '/home/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/user/:id',
      name: 'user',
      component: () => import('@/views/UserView.vue'),
    },
    {
      path: '/me',
      name: 'self',
      component: () => import('@/views/UserView.vue'),
    },
    {
      path: '/rooms',
      name: 'rooms',
      component: () => import('@/views/RoomListView.vue'),
    },
    {
      path: '/challenges',
      name: 'challenges',
      component: () => import('@/views/ChallengesView.vue'),
    },
    {
      path: '/game/:id',
      name: 'game',
      component: () => import('@/views/GameView.vue'),
    },
    {
      path: '/top',
      name: 'leaderboard',
      component: () => import('@/views/LeaderboardView.vue'),
    },
    {
      path: '/room/:id',
      name: 'room',
      component: () => import('@/views/RoomView.vue'),
    },
  ],
})

export default router
