<template>
  <div class="page-wrap">
    <div class="top-right"><button @click="toggleTheme">{{ theme === 'light' ? '🌙 深色' : '☀️ 浅色' }}</button></div>
    <div class="card">
      <div class="card-left">
        <h1>重置密码</h1>
        <p>输入你的邮箱以接收重置指引</p>
        <form @submit.prevent="submit" class="form">
          <label>邮箱<input v-model="email" required /></label>
          <div class="error" v-if="error">{{ error }}</div>
          <div class="success" v-if="message">{{ message }}</div>
          <button class="btn" type="submit">{{ loading ? '提交中...' : '发送重置邮件' }}</button>
          <div class="help" style="margin-top:8px">
            <router-link to="/login">返回登录</router-link>
          </div>
        </form>
      </div>
      <div class="card-right"><div class="promo"><h2>不用担心</h2><p>如果邮箱存在，会发送重置指引（取决于后端）。</p></div></div>
    </div>
  </div>
</template>

<script setup>
/**
 * 忘记密码页面
 * 处理密码重置请求功能
 */
import { ref, inject } from 'vue'
import { requestPasswordReset } from '../../shared/utils/auth'

// 响应式数据
const email = ref('')
const loading = ref(false)
const error = ref('')
const message = ref('')

// 主题提供者
const { theme, toggleTheme } = inject('theme')

// 提交重置请求
const submit = async () => {
  loading.value = true
  error.value = ''
  message.value = ''
  try {
    await requestPasswordReset({ email: email.value })
    message.value = '如果该邮箱存在，已发送重置邮件。'
  } catch (e) {
    error.value = e.response?.data?.detail || '请求失败'
  } finally {
    loading.value = false
  }
}
</script>
