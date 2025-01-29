import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/LeaderboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/me',
      name: 'user',
      component: () => import("@/views/UserView.vue")
    },
    {
      path: '/lobby',
      name: 'lobby',
      component: () => import("@/views/LobbyListView.vue")
    },
    {
      path: '/challenges',
      name: 'challenges',
      component: () => import("@/views/ChallengesView.vue")
    },
    {
      path: '/game/:id',
      name: 'game',
      component: () => import("@/views/GameView.vue")
    },
    {
      path: '/top',
      name: 'leaderboard',
      component: () => import("@/views/LeaderboardView.vue")
    },
    {
      path: '/lobby/:id',
      name: 'lobby',
      component: () => import("@/views/LobbyView.vue")
    },

  ],
})

export default router
