import App from '@/app/App.vue'

import router from '@/app/router'
import { useUserStore } from '@/share/stores/user'

import { createPinia } from 'pinia'
import { createApp } from 'vue'
import '@/app/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const userStore = useUserStore()
router.beforeEach((to) => {
  if (to.fullPath === '/' || to.fullPath === '/login/' || userStore.userId) {
    return true
  } else {
    return '/login/'
  }
})

app.mount('#app')
