// shared/utils/csrf.js - CSRF工具函数
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/backend'

// 读取Cookie函数
export function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

// 手动初始化CSRF token（应用启动时调用）
export async function initializeCSRF() {
  try {
    const response = await axios.get(`${API_BASE}/csrf/`, {
      withCredentials: true
    })
    console.log('CSRF token initialized successfully')
    return response.data.csrfToken
  } catch (error) {
    console.error('CSRF initialization failed:', error)
    throw error
  }
}

// 获取当前CSRF token（从cookie）
export function getCurrentCSRFToken() {
  return getCookie('csrftoken')
}

// 检查CSRF token是否存在
export function hasCSRFToken() {
  return !!getCurrentCSRFToken()
}

// 手动刷新CSRF token
export async function refreshCSRFToken() {
  try {
    await axios.get(`${API_BASE}/csrf/`, {
      withCredentials: true
    })
    console.log('CSRF token refreshed')
    return getCookie('csrftoken')
  } catch (error) {
    console.error('CSRF refresh failed:', error)
    throw error
  }
}