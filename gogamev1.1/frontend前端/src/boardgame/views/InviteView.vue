<template>
  <div class="invite-view">
    <!-- 顶部用户信息卡片 -->
    <div class="user-info-card">
      <div class="card-header">
        <div class="user-avatar">
          <div class="avatar-circle">{{ currentUsername?.[0]?.toUpperCase() || '?' }}</div>
        </div>
        <div class="user-details">
          <h2 class="username">{{ currentUsername || '加载中...' }}</h2>
          <div class="server-selector">
            <span class="label">服务区:</span>
            <select v-model="userServer" @change="handleServerChange" class="server-select">
              <option value="a">A区</option>
              <option value="b">B区</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索用户区域 -->
    <div class="search-section">
      <div class="section-title">
        <h3>搜索同服用户</h3>
      </div>
      <div class="search-box">
        <input
          v-model="searchKeyword"
          @input="handleSearch"
          placeholder="输入用户名搜索..."
          class="search-input"
        />
        <button class="search-btn" @click="searchUsers">
          <span v-if="!searching">🔍</span>
          <span v-else class="spinner">⟳</span>
        </button>
      </div>
      <div class="search-results">
        <div v-if="users.length === 0 && searchKeyword" class="empty-state">
          未找到用户
        </div>
        <div v-for="user in users" :key="user.id" class="user-item">
          <div class="user-info">
            <span class="user-name">{{ user.username }}</span>
          </div>
          <button
            class="invite-btn"
            @click="sendInvite(user)"
            :disabled="invitingUsers.has(user.username)"
          >
            <span v-if="invitingUsers.has(user.username)" class="spinner small">⟳</span>
            <span v-else>✉️ 邀请</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 邀请列表区域 -->
    <div class="invitations-section">
      <!-- 已发邀请 -->
      <div class="invitation-column">
        <h3 class="column-title">
          <span class="icon">📤</span>
          我发出的邀请
        </h3>
        <div class="invitation-list">
          <div v-if="sentInvitations.length === 0" class="empty-state">
            暂无发出的邀请
          </div>
          <div
            v-for="inv in sentInvitations"
            :key="inv.id"
            class="invitation-card sent"
          >
            <div class="invitation-header">
              <span class="invitee-name">👤 {{ inv.invitee_username }}</span>
              <span class="status-badge" :class="{ confirmed: inv.is_confirmed }">
                {{ inv.is_confirmed ? '✓ 已确认' : '⏳ 等待中' }}
              </span>
            </div>
            <div class="invitation-meta">
              <span class="time">🕐 {{ formatTime(inv.created_at) }}</span>
            </div>
            <button
              class="delete-btn"
              @click="handleDeleteInvitation(inv.id)"
              :disabled="deletingId === inv.id"
            >
              <span v-if="deletingId === inv.id" class="spinner small">⟳</span>
              <span v-else>🗑 删除</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 收到邀请 -->
      <div class="invitation-column">
        <h3 class="column-title">
          <span class="icon">📥</span>
          收到的邀请
        </h3>
        <div class="invitation-list">
          <div v-if="receivedInvitations.length === 0" class="empty-state">
            暂无收到的邀请
          </div>
          <div
            v-for="inv in receivedInvitations"
            :key="inv.id"
            class="invitation-card received"
          >
            <div class="invitation-header">
              <span class="inviter-name">👤 {{ inv.inviter_username }}</span>
              <span class="status-badge">🎯 邀请对战</span>
            </div>
            <div class="invitation-meta">
              <span class="time">🕐 {{ formatTime(inv.created_at) }}</span>
            </div>
            <button class="confirm-btn" @click="confirmInvitation(inv.id)">✓ 确认对战</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../shared/utils/auth'

// 响应式数据
const router = useRouter()
const currentUsername = ref('')
const userServer = ref('a')
const searchKeyword = ref('')
const users = ref([])
const sentInvitations = ref([])
const receivedInvitations = ref([])
const searching = ref(false)
const invitingUsers = ref(new Set())
const deletingId = ref(null)

// 搜索用户（防抖）
let searchTimeout = null
const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchKeyword.value.trim()) {
      searchUsers()
    } else {
      users.value = []
    }
  }, 300)
}

// 搜索用户
const searchUsers = async () => {
  if (!searchKeyword.value.trim()) return

  searching.value = true
  try {
    const res = await api.get(`/invitation/search-users/?keyword=${searchKeyword.value}`)
    if (res.data.success) {
      users.value = res.data.data.users
      currentUsername.value = res.data.data.current_user_server.username
      userServer.value = res.data.data.current_user_server.server
    }
  } catch (error) {
    console.error('搜索失败:', error)
    users.value = []
  } finally {
    searching.value = false
  }
}

// 设置服务区
const handleServerChange = async () => {
  try {
    await api.post('/invitation/set-server/', { server: userServer.value })
    // 可添加成功提示
  } catch (error) {
    console.error('设置服务区失败:', error)
    // 可添加错误提示
  }
}

// 发送邀请
const sendInvite = async (user) => {
  invitingUsers.value.add(user.username)
  try {
    await api.post('/invitation/create/', { invitee_username: user.username })
    await loadSentInvitations()
    // 可添加成功提示
  } catch (error) {
    console.error('发送邀请失败:', error)
    // 可添加错误提示
  } finally {
    invitingUsers.value.delete(user.username)
  }
}

// 删除邀请
const deleteInvitation = async (id) => {
  try {
    await api.delete(`/invitation/delete/${id}/`)
    await loadSentInvitations()
  } catch (error) {
    console.error('删除邀请失败:', error)
  }
}

// 带加载状态的删除邀请
const handleDeleteInvitation = async (id) => {
  deletingId.value = id
  try {
    await deleteInvitation(id)
  } finally {
    deletingId.value = null
  }
}

// 确认邀请
const confirmInvitation = async (id) => {
  try {
    // 1. 确认邀请
    await api.post(`/invitation/confirm/${id}/`)

    // 2. 获取邀请信息以找到邀请者用户名
    const invitation = receivedInvitations.value.find(inv => inv.id === id)
    if (!invitation) {
      console.error('找不到邀请信息')
      return
    }

    // 3. 获取当前用户名
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    if (!userInfo.username) {
      console.error('找不到当前用户信息')
      return
    }

    // 4. 创建新游戏（被邀请者执黑棋，邀请者执白棋）
    const gameData = {
      player1: userInfo.username,  // 当前用户（被邀请者）执黑棋
      player2: invitation.inviter_username,  // 邀请者执白棋
      winner: "",  // 新游戏没有获胜者
      score_black: "0.00",
      score_white: "0.00",
      komi: "3.75"
    }

    const gameResponse = await api.post('/datab/games/', gameData)
    const newGameId = gameResponse.data.id

    // 5. 刷新游戏数据以同步新创建的游戏
    console.log('邀请确认成功，正在刷新游戏数据...')
    try {
      // 导入 gameStore 并刷新数据
      const { useGameStore } = await import('../../stores/gameStore')
      const gameStore = useGameStore()

      // 强制刷新游戏列表，确保新游戏能立即显示
      await gameStore.forceRefreshIncompleteGames()
      console.log('游戏列表刷新完成，新创建的游戏已同步到列表')

      // 立即刷新新游戏的执棋状态信息
      console.log('正在刷新新游戏的执棋状态信息...')
      const refreshResult = await gameStore.refreshGameInfo(newGameId)
      if (refreshResult.success) {
        console.log('新游戏执棋状态刷新成功:', refreshResult.data)
        console.log(`玩家角色: ${refreshResult.data.playerColor}, 最新落子: ${refreshResult.data.latestMoveColor}`)
      } else {
        console.error('新游戏执棋状态刷新失败:', refreshResult.error)
      }
    } catch (refreshError) {
      console.error('刷新游戏数据失败:', refreshError)
      // 不影响主流程，只记录错误
    }

    // 6. 跳转到HistoryView并选中新建的游戏
    router.push({
      path: '/history',
      query: {
        fromInvite: 'true',
        gameId: newGameId,
        invitationId: id // 添加邀请ID参数，用于后续自动删除
      }
    })

    await loadReceivedInvitations()
  } catch (error) {
    console.error('确认邀请失败:', error)
    if (error.response?.status === 400) {
      alert('确认邀请失败：' + (error.response.data?.detail || '请求参数错误'))
    } else if (error.response?.status === 401) {
      alert('认证失败，请重新登录')
    } else {
      alert('确认邀请失败，请重试')
    }
  }
}

// 加载已发邀请
const loadSentInvitations = async () => {
  try {
    const res = await api.get('/invitation/sent-invitations/')
    if (res.data.success) {
      sentInvitations.value = res.data.data
    }
  } catch (error) {
    console.error('加载已发邀请失败:', error)
  }
}

// 加载收到邀请
const loadReceivedInvitations = async () => {
  try {
    const res = await api.get('/invitation/received-invitations/')
    if (res.data.success) {
      receivedInvitations.value = res.data.data
    }
  } catch (error) {
    console.error('加载收到邀请失败:', error)
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (minutes < 1440) return `${Math.floor(minutes / 60)}小时前`
  return `${Math.floor(minutes / 1440)}天前`
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const res = await api.get('/invitation/search-users/?keyword=')
    if (res.data.success) {
      currentUsername.value = res.data.data.current_user_server.username
      userServer.value = res.data.data.current_user_server.server
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 初始化
onMounted(async () => {
  await loadUserInfo()
  await loadSentInvitations()
  await loadReceivedInvitations()
})
</script>

<style scoped>
.invite-view {
  padding: 20px;
  background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
  min-height: 100vh;
  color: #0b1320;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 1000px;
  margin: 0 auto;
}

/* 用户信息卡片 */
.user-info-card {
  background: linear-gradient(180deg, #ffffff, #f6f9ff);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(12, 20, 30, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar .avatar-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c5cff 0%, #9d7cff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(124, 92, 255, 0.3);
}

.user-details {
  flex: 1;
}

.username {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: #0b1320;
}

.server-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.server-selector .label {
  font-size: 14px;
  color: #3f5160;
}

.server-select {
  background: rgba(12, 20, 30, 0.05);
  border: 1px solid rgba(12, 20, 30, 0.1);
  border-radius: 6px;
  padding: 8px 14px;
  color: #0b1320;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.server-select:hover {
  background: rgba(12, 20, 30, 0.08);
  border-color: #7c5cff;
}

.server-select:focus {
  outline: none;
  background: rgba(12, 20, 30, 0.08);
  border-color: #7c5cff;
}

.server-select option {
  background: #ffffff;
  color: #0b1320;
}

/* 搜索区域 */
.search-section {
  background: linear-gradient(180deg, #ffffff, #f6f9ff);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(12, 20, 30, 0.1);
}

.section-title h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #0b1320;
  font-weight: 600;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: center;
}

.search-input {
  flex: 0 0 75%;
  width: 75%;
  background: rgba(12, 20, 30, 0.05);
  border: 1px solid rgba(12, 20, 30, 0.1);
  border-radius: 8px;
  padding: 12px 16px;
  color: #0b1320;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  height: 44px;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: #9aa4b2;
}

.search-input:focus {
  background: rgba(12, 20, 30, 0.08);
  border-color: #7c5cff;
  box-shadow: 0 0 0 2px rgba(124, 92, 255, 0.1);
}

.search-btn {
  background: #7c5cff;
  border: none;
  border-radius: 8px;
  padding: 12px 18px;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 600;
  height: 44px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  width:20%;
}

.search-btn:hover {
  background: #9d7cff;
  transform: translateY(-1px);
}

.search-btn:active {
  transform: translateY(0);
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-item {
  background: rgba(12, 20, 30, 0.05);
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
  border: 1px solid rgba(12, 20, 30, 0.1);
}

.user-item:hover {
  background: rgba(12, 20, 30, 0.08);
  border-color: #7c5cff;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 16px;
  color: #0b1320;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.invite-btn {
  background: #7c5cff;
  border: none;
  border-radius: 6px;
  padding: 8px 14px;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.invite-btn:hover:not(:disabled) {
  background: #9d7cff;
  transform: translateY(-1px);
}

.invite-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 邀请列表区域 - 上下布局 */
.invitations-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.invitation-column {
  background: linear-gradient(180deg, #ffffff, #f6f9ff);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(12, 20, 30, 0.1);
}

.column-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #0b1320;
  font-weight: 600;
}

.column-title .icon {
  font-size: 20px;
}

.invitation-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.invitation-card {
  background: #333333;
  border-radius: 8px;
  padding: 14px;
  border-left: 3px solid;
  transition: all 0.2s;
  border: 1px solid #404040;
}

.invitation-card.sent {
  border-left-color: #cc884a;
}

.invitation-card.received {
  border-left-color: #d4a574;
}

.invitation-card:hover {
  background: #404040;
  transform: translateX(3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.invitation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.invitee-name,
.inviter-name {
  font-weight: 600;
  font-size: 15px;
  color: #fff;
}

.status-badge {
  background: #404040;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  color: #d4a574;
}

.status-badge.confirmed {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.invitation-meta {
  margin-bottom: 10px;
}

.time {
  font-size: 13px;
  color: #a3a3a3;
}

.delete-btn,
.confirm-btn {
  background: #e57373;
  border: none;
  border-radius: 6px;
  padding: 8px 14px;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover:not(:disabled) {
  background: #ef5350;
  transform: translateY(-1px);
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-btn {
  background: #4caf50;
}

.confirm-btn:hover {
  background: #66bb6a;
  transform: translateY(-1px);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 24px;
  color: #737373;
  font-size: 14px;
}

/* 旋转动画 */
.spinner {
  animation: spin 1s linear infinite;
}

.spinner.small {
  font-size: 12px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    text-align: center;
  }

  .invite-view {
    padding: 12px;
  }

  .user-item {
    flex-wrap: wrap;
  }

  .invite-btn {
    margin-top: 8px;
  }
}
</style>
