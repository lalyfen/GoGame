import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/LoginView.vue'
import Register from '../views/RegisterView.vue'
import Forgot from '../views/ForgotView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/forgot', component: Forgot },
]

const router = createRouter({
  history: createWebHistory('/auth.html'),
  routes
})

router.beforeEach((to, from, next) => {
  const requires = to.meta.requiresAuth
  const hasToken = !!localStorage.getItem('access')
  if (requires && !hasToken) next('/login')
  else next()
})

export default router
