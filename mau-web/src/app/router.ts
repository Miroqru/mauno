import LendingPage from '@/pages/LendingPage.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'lending',
      component: LendingPage,
    },
    {
      path: '/home/',
      name: 'home',
      component: () => import('@/pages/HomePage.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
    },
    {
      path: '/user/:id',
      name: 'user',
      component: () => import('@/pages/UserPage.vue'),
    },
    {
      path: '/me',
      name: 'self',
      component: () => import('@/pages/UserPage.vue'),
    },
    {
      path: '/rooms',
      name: 'rooms',
      component: () => import('@/pages/RoomListPage.vue'),
    },
    {
      path: '/challenges',
      name: 'challenges',
      component: () => import('@/pages/ChallengesPage.vue'),
    },
    {
      path: '/game/',
      name: 'game',
      component: () => import('@/pages/GamePage.vue'),
    },
    {
      path: '/top',
      name: 'leaderboard',
      component: () => import('@/pages/LeaderboardPage.vue'),
    },
    {
      path: '/room/:id',
      name: 'room',
      component: () => import('@/pages/RoomPage.vue'),
    },
  ],
})

export default router
