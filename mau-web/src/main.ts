import { createPinia } from 'pinia'

import { createApp } from 'vue'
import App from './App.vue'

import router from './router'
import { useUserStore } from './stores/user'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const userStore = useUserStore()
router.beforeEach((to) => {
  if (to.fullPath === '/' || to.fullPath === '/login/' || userStore.userId) {
    return true
  }
  else {
    return '/login/'
  }
})

app.mount('#app')
