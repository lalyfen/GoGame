/**
 * 主题管理组合式函数
 * 提供主题切换功能，支持本地存储
 */
import { ref } from 'vue'

export function useTheme() {
  // 主题状态，默认从本地存储读取或使用'light'
  const theme = ref(localStorage.getItem('theme') || 'light')

  // 切换主题
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
  }

  // 设置特定主题
  const setTheme = (newTheme) => {
    if (newTheme === 'light' || newTheme === 'dark') {
      theme.value = newTheme
      localStorage.setItem('theme', theme.value)
    }
  }

  return {
    theme,
    toggleTheme,
    setTheme
  }
}