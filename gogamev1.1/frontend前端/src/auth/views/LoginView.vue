<template>
  <div class="page-wrap">
    <div class="top-right"><button @click="toggleTheme">{{ theme === 'light' ? '🌙 深色' : '☀️ 浅色' }}</button></div>
    <div class="card">
      <div class="card-left">
        <h1>欢迎回到 Vue Auth</h1>
        <p>使用账号登录以访问受保护资源</p>
        <form @submit.prevent="submit" class="form">
          <label>用户名<input v-model="username" required /></label>
          <label>密码<input type="password" v-model="password" required /></label>
          <div class="error" v-if="error">{{ error }}</div>
          <button class="btn" type="submit">{{ loading ? '登录中...' : '登录' }}</button>
          <div class="help"><router-link to="/forgot">忘记密码?</router-link><router-link to="/register">注册新账号</router-link></div>
        </form>
      </div>
      <div class="card-right"><div class="promo"><h2>安全 · 快速</h2><p>基于 JWT 的认证示例。</p></div></div>
    </div>
  </div>
</template>

<script setup>
/**
 * 登录页面
 * 处理用户登录功能
 */
import { ref, inject } from 'vue'
import { login } from '../../shared/utils/auth'
import { useRouter } from 'vue-router'

// 响应式数据
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

// 路由和主题
const router = useRouter()
const { theme, toggleTheme } = inject('theme')

// 登录提交
const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    await login({ username: username.value, password: password.value })
    // 登录成功后跳转到围棋游戏页面
    window.location.href = '/boardgame.html'
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
