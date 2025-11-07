import { createApp } from 'vue'
import App from './Auth.vue'
import router from './router'
import '../assets/auth.css'
import { initializeCSRF } from '../shared/utils/csrf'

// 初始化CSRF token
initializeCSRF().catch(error => {
  console.error('Failed to initialize CSRF on app startup:', error)
})

// 直接挂载应用
createApp(App).use(router).mount('#app')
