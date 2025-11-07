<template>
  <div :class="['app', theme]">
    <router-view />  <!--路由出口 -->
  </div>
</template>

<script setup>
/**
 * 认证模块根组件
 * 提供主题切换功能
 */
import { provide, watch } from 'vue'
import { useTheme } from '../shared/composables/useTheme'

// 使用主题组合式函数
const { theme, toggleTheme } = useTheme()

// 监听主题变化，应用到body元素
watch(theme, (newTheme) => {
  // 移除所有主题类
  document.body.classList.remove('theme-light', 'theme-dark')
  // 添加当前主题类
  document.body.classList.add(`theme-${newTheme}`)
}, { immediate: true })

// 提供主题给子组件
provide('theme', { theme, toggleTheme })
</script>
