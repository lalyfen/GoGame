<template>
  <div class="logout-view">
    <!-- 登出确认对话框 -->
    <LogoutModal
      :visible="showLogoutModal"
      @close="handleCancel"
      @confirm="handleLogoutConfirm"
    />
  </div>
</template>

<script setup>
/**
 * 登出页面
 * 显示登出确认对话框并处理登出逻辑
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { logout } from '../../shared/utils/auth'
import LogoutModal from '../components/LogoutModal.vue'

const router = useRouter()
const showLogoutModal = ref(false)

// 页面加载时自动显示登出确认对话框
onMounted(() => {
  showLogoutModal.value = true
})

// 处理取消登出
const handleCancel = () => {
  // 返回上一页或游戏主页
  router.back()
}

// 处理确认登出
const handleLogoutConfirm = async () => {
  try {
    await logout()
    // 登出成功后跳转到登录页面
    window.location.href = '/auth.html#/login'
  } catch (error) {
    console.error('登出失败:', error)
    // 即使登出失败，也跳转到登录页面
    window.location.href = '/auth.html#/login'
  }
}
</script>

<style scoped>
.logout-view {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
