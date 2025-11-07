import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './BoardGame.vue';
import '../assets/boardgame.css';
import { initializeCSRF } from '../shared/utils/csrf';
import router from './router';

// 创建 Pinia 实例
const pinia = createPinia();

// 检查是否有访问令牌
const token = localStorage.getItem('access');
if (!token) {
  // 如果没有令牌，重定向到登录页面
  window.location.href = '/auth.html#/login';
} else {
  // 初始化CSRF token
  initializeCSRF().catch(error => {
    console.error('Failed to initialize CSRF:', error);
  });

  // 如果有令牌，挂载应用
  createApp(App)
    .use(pinia)  // 添加 Pinia
    .use(router)
    .mount('#app');
}
