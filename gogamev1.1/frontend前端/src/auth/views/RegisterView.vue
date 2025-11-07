<template>
  <div class="page-wrap">
    <div class="top-right"><button @click="toggleTheme">{{ theme === 'light' ? '🌙 深色' : '☀️ 浅色' }}</button></div>
    <div class="card">
      <div class="card-left">
        <h1>注册新用户</h1>
        <p>创建你的账号</p>
        <form @submit.prevent="submit" class="form">
          <label>用户名<input v-model="username" required /></label>
          <label>邮箱<input v-model="email" required /></label>
          <label>密码<input type="password" v-model="password" required /></label>
          <div class="error" v-if="error">{{ error }}</div>
          <div class="success" v-if="success">{{ success }}</div>
          <button class="btn" type="submit">{{ loading ? '注册中...' : '注册' }}</button>
          <div class="help" style="margin-top:8px">
            <router-link to="/login">返回登录</router-link>
          </div>
        </form>
      </div>
      <div class="card-right"><div class="promo"><h2>欢迎加入</h2><p>注册后请登录。</p></div></div>
    </div>
  </div>
</template>

<script setup>
/**
 * 注册页面
 * 处理用户注册功能
 */
import { ref, inject } from 'vue'
import { register } from '../../shared/utils/auth'
import { useRouter } from 'vue-router'

// 响应式数据
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

// 路由和主题
const router = useRouter()
const { theme, toggleTheme } = inject('theme')

// 注册提交
const submit = async () => {
  loading.value = true
  error.value = ''
  try {
    await register({ username: username.value, email: email.value, password: password.value })
    success.value = '注册成功，请登录'
    setTimeout(() => router.push('/login'), 1000)
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>
