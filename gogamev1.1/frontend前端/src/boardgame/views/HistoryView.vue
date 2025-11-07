<template>
  <div class="history-view">
    <!-- 用户信息区域 -->
    <div class="user-info-section">
      <div class="user-header">
        <div class="avatar-circle">{{ currentUsername?.[0]?.toUpperCase() || '?' }}</div>
        <h2 class="username">{{ currentUsername || '加载中...' }}</h2>
      </div>
    </div>

    <!-- 对局列表区域 -->
    <div class="game-list-section">
      <div class="section-header">
        <h3 class="section-title">未完成的对局</h3>
        <button
          class="refresh-all-btn"
          @click="handleRefreshAll"
          :disabled="refreshingAll || incompleteGames.length === 0"
          title="刷新所有对局信息">
          <span v-if="refreshingAll" class="loading-spinner">⟳</span>
          <span v-else class="refresh-icon">↻</span>
          <span class="refresh-text">刷新所有</span>
        </button>
      </div>
      <div v-if="gameStore.isLoadingGame" class="loading">加载棋局中...</div>
      <div v-else-if="gameStore.loading" class="loading">加载中...</div>
      <div v-else-if="incompleteGames.length === 0" class="empty-state">暂无未完成的对局</div>
      <div v-else class="game-list">
        <div v-for="game in incompleteGames" :key="game.id"
             class="game-item"
             :class="{ active: gameStore.selectedGameId === game.id }"
             @click="selectGame(game.id)">
          <div class="game-info">
            <div class="game-id">对局 {{ game.id }}</div>
            <div class="game-opponent">vs {{ getOpponentName(game) }}</div>
            <div class="game-time">{{ formatTime(game.created_at) }}</div>
            <div class="game-status">
              {{ getGameStatus(game) }}
              <span v-if="getTurnInfo(game)" class="turn-info" :class="getTurnInfo(game).class">
                {{ getTurnInfo(game).text }}
              </span>
            </div>
          </div>
          <button
            class="refresh-btn"
            @click.stop="handleRefreshGame(game.id)"
            :disabled="gameStore.isRefreshing(game.id)"
            title="刷新对局信息">
            <span v-if="gameStore.isRefreshing(game.id)" class="loading-spinner small">⟳</span>
            <span v-else class="refresh-icon small">↻</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 已完成对局列表区域 -->
    <div class="game-list-section" v-if="completedGames.length > 0 || gameStore.loading">
      <div class="section-header">
        <h3 class="section-title">已结束的对局</h3>
      </div>
      <div v-if="completedGames.length === 0 && !gameStore.loading" class="empty-state">暂无已结束的对局</div>
      <div v-else class="game-list">
        <div v-for="game in completedGames" :key="game.id"
             class="game-item"
             :class="{ active: gameStore.selectedGameId === game.id }"
             @click="selectGame(game.id)">
          <div class="game-info">
            <div class="game-id">对局 {{ game.id }}</div>
            <div class="game-opponent">vs {{ getOpponentName(game) }}</div>
            <div class="game-time">{{ formatTime(game.updated_at) }}</div>
            <div class="game-status">
              {{ getWinnerInfo(game) }}
              <span class="score-info">{{ getScoreInfo(game) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态显示 -->
    <div v-if="!gameStore.loading && incompleteGames.length === 0 && completedGames.length === 0" class="empty-state-container">
      <div class="empty-icon">🎯</div>
      <h3>暂无对局</h3>
      <p>您当前没有进行中的围棋对局</p>
      <p>可以前往邀请页面开始新的对局</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../shared/utils/auth'
import { useGameStore } from '../../stores/gameStore'

// 使用Pinia store
const gameStore = useGameStore()

// 响应式数据
const userId = ref(null) // 当前用户ID
const currentUsername = ref('') // 当前用户名
const refreshingAll = ref(false) // 全局刷新状态

// 路由检测
const route = useRoute()

// 计算属性 - 从store获取数据
const incompleteGames = computed(() => gameStore.incompleteGames)
const completedGames = computed(() => gameStore.completedGames)
const loading = computed(() => gameStore.loading)
const error = computed(() => gameStore.error)

// 用户信息缓存
const userInfoCache = ref(new Map())

// 选择对局并加载到主棋盘
const selectGame = async (gameId) => {
  try {
    console.log('选择棋局，将在主棋盘显示:', gameId)
    // 调用store的方法加载棋局数据，这会触发BoardGame中的watch
    await gameStore.loadSelectedGame(gameId)
  } catch (error) {
    console.error('加载棋局失败:', error)
  }
}

// 获取对手名称
const getOpponentName = (game) => {
  console.log('getOpponentName被调用, userId:', userId.value, 'game:', game)

  // 如果userId还没有加载，显示临时值
  if (!userId.value || userId.value === 'unknown') {
    console.log('userId还未加载或为unknown')
    return '加载中...'
  }

  // 从游戏数据中直接获取对手用户名（因为player1和player2已经是用户名）
  const opponentName = game.player1 === userId.value ? game.player2 : game.player1
  console.log('获取到对手用户名:', opponentName)

  return opponentName
}

// 异步加载对手用户名
const loadOpponentName = async (opponentId) => {
  if (userInfoCache.value.has(opponentId)) return

  try {
    console.log('正在获取用户信息:', opponentId)
    // 尝试使用不同的API端点
    const response = await api.get(`/datab/users/${opponentId}/`)
    const username = response.data.username || response.data.name || `用户${opponentId}`
    userInfoCache.value.set(opponentId, username)
    console.log('获取到用户名:', username)
  } catch (error) {
    console.error('获取对手用户名失败，尝试其他API:', error)
    try {
      // 尝试从游戏数据中获取用户名
      const game = incompleteGames.value.find(g =>
        g.player1 === opponentId || g.player2 === opponentId
      )
      if (game && game.player1_name && game.player2_name) {
        const username = game.player1 === opponentId ? game.player1_name : game.player2_name
        userInfoCache.value.set(opponentId, username)
        console.log('从游戏数据获取到用户名:', username)
      } else {
        userInfoCache.value.set(opponentId, `用户${opponentId}`)
      }
    } catch (fallbackError) {
      console.error('备用方案也失败:', fallbackError)
      userInfoCache.value.set(opponentId, `用户${opponentId}`)
    }
  }
}

// 获取游戏状态
const getGameStatus = (game) => {
  if (gameStore.selectedGameId === game.id && gameStore.isLoadingGame) {
    return '加载中...'
  }
  return '进行中'
}

// 获取轮次信息
const getTurnInfo = (game) => {
  const gameInfo = gameStore.getGameInfoCache(game.id)
  if (!gameInfo || !gameInfo.playerColor) {
    return null
  }

  const isMyTurn = gameStore.getIsMyTurn(game.id)
  if (isMyTurn === null) {
    return null
  }

  if (isMyTurn) {
    return {
      text: '轮到您',
      class: 'my-turn'
    }
  } else {
    return {
      text: '等待对手',
      class: 'opponent-turn'
    }
  }
}

// 刷新单个游戏信息
const handleRefreshGame = async (gameId) => {
  try {
    console.log(`刷新游戏 ${gameId} 的信息`)
    const result = await gameStore.refreshGameInfo(gameId)

    if (result.success) {
      console.log('游戏信息刷新成功')
    } else {
      console.error('游戏信息刷新失败:', result.error)
    }
  } catch (error) {
    console.error('刷新游戏信息时发生错误:', error)
  }
}

// 刷新所有游戏信息
const handleRefreshAll = async () => {
  try {
    console.log('开始刷新所有游戏信息')
    refreshingAll.value = true

    const result = await gameStore.refreshAllGames()

    if (result.success) {
      console.log(`批量刷新完成: ${result.successful}/${result.total} 个游戏成功`)
    } else {
      console.error('批量刷新失败:', result.error)
    }
  } catch (error) {
    console.error('批量刷新时发生错误:', error)
  } finally {
    refreshingAll.value = false
  }
}


// 加载当前用户信息
const loadCurrentUserInfo = async () => {
  try {
    // 从登录时存储的用户信息中获取
    let userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    console.log('从localStorage读取的用户信息:', userInfo)

    // 如果用户信息不完整，尝试从token中解析或者重新设置
    if (!userInfo.username) {
      console.log('用户信息不完整，尝试从token获取或重新设置')
      const token = localStorage.getItem('access')
      if (token) {
        // 如果有token但没有用户信息，设置默认值
        userInfo = { username: '用户', id: '用户' }
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
      }
    }

    if (userInfo.username) {
      currentUsername.value = userInfo.username
      userId.value = userInfo.id || userInfo.username // 使用用户名作为ID
      console.log('成功获取用户信息:', { username: currentUsername.value, id: userId.value })
      return
    }

    // 如果localStorage中没有，设置默认值
    console.log('localStorage中没有用户信息，使用默认值')
    currentUsername.value = '用户'
    userId.value = 'unknown'

  } catch (error) {
    console.error('获取用户信息失败:', error)
    currentUsername.value = '未知用户'
    userId.value = 'unknown'
  }
}

// 预加载所有对手的用户信息
const preloadOpponentsInfo = async () => {
  // 暂时禁用，因为API路径不确定
  console.log('预加载对手信息功能暂时禁用，等待API路径确认')
}

// 路由进入逻辑处理
const handleRouteEntry = async () => {
  console.log('HistoryView路由进入逻辑处理...')

  // 优先加载当前用户信息
  await loadCurrentUserInfo()

  // 确保数据已加载（如果需要）
  if (gameStore.incompleteGames.length === 0 && !gameStore.loading) {
    console.log('Store中没有未完成对局数据，开始加载...')
    await gameStore.loadIncompleteGames()
  }

  // 同时加载已完成对局数据
  if (gameStore.completedGames.length === 0 && !gameStore.loading) {
    console.log('Store中没有已完成对局数据，开始加载...')
    await gameStore.loadCompletedGames()
  }

  // 预加载对手信息（暂时禁用）
  // if (incompleteGames.value.length > 0) {
  //   await preloadOpponentsInfo()
  // }

  // 检查是否从邀请确认进入
  if (route.query.fromInvite === 'true' && route.query.gameId) {
    // 情况(1): 从邀请确认进入
    const newGameId = parseInt(route.query.gameId)
    console.log('从邀请确认进入，新对局ID:', newGameId)

    // 选择新创建的对局
    await selectGame(newGameId)

    // 确保执棋状态信息已刷新（防止邀请页面刷新失败的情况）
    console.log('确保新游戏的执棋状态信息已更新...')
    try {
      const refreshResult = await gameStore.refreshGameInfo(newGameId)
      if (refreshResult.success) {
        console.log('HistoryView: 新游戏执棋状态确认刷新成功:', refreshResult.data)
      } else {
        console.warn('HistoryView: 新游戏执棋状态确认刷新失败:', refreshResult.error)
      }
    } catch (error) {
      console.error('HistoryView: 确认刷新执棋状态时发生错误:', error)
    }

  } else if (incompleteGames.value.length > 0) {
    // 情况(2): 普通进入，选择第一个对局
    console.log('普通进入HistoryView，选择第一个对局')
    await selectGame(incompleteGames.value[0].id)
  }
}

// 时间格式化
const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

// 获取胜者信息
const getWinnerInfo = (game) => {
  if (game.winner === 'black') {
    return '黑棋胜'
  } else if (game.winner === 'white') {
    return '白棋胜'
  } else if (game.winner === 'draw') {
    return '平局'
  } else {
    return '已结束'
  }
}

// 获取比分信息
const getScoreInfo = (game) => {
  const blackScore = game.score_black || '0.00'
  const whiteScore = game.score_white || '0.00'
  return `黑 ${blackScore} : 白 ${whiteScore}`
}

// 组件挂载时处理路由逻辑
onMounted(handleRouteEntry)
</script>

<style scoped>
.history-view {
  padding: 20px;
  background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
  min-height: 100vh;
  color: #0b1320;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 400px;
  margin: 0 auto;
}

.user-info-section {
  background: linear-gradient(180deg, #ffffff, #f6f9ff);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(12, 20, 30, 0.1);
  margin-bottom: 20px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(180deg, #7c5cff, #6b4ee8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.username {
  margin: 0;
  font-size: 18px;
  color: #0b1320;
  font-weight: 600;
}

.game-list-section {
  background: linear-gradient(180deg, #ffffff, #f6f9ff);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(12, 20, 30, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  margin: 0;
  font-size: 18px;
  color: #0b1320;
  font-weight: 600;
}

.refresh-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #7c5cff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.refresh-all-btn:hover:not(:disabled) {
  background: #6b4ee8;
  transform: translateY(-1px);
}

.refresh-all-btn:disabled {
  background: #9aa4b2;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
}

.loading-spinner.small {
  font-size: 12px;
}

.refresh-icon {
  font-size: 16px;
}

.refresh-icon.small {
  font-size: 14px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.game-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.game-item {
  background: rgba(12, 20, 30, 0.05);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid rgba(12, 20, 30, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.game-item:hover {
  background: rgba(12, 20, 30, 0.08);
  border-color: #7c5cff;
}

.game-item.active {
  background: rgba(124, 92, 255, 0.1);
  border-color: #7c5cff;
}

.game-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.refresh-btn {
  background: transparent;
  border: 1px solid #9aa4b2;
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
  color: #3f5160;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
}

.refresh-btn:hover:not(:disabled) {
  background: #7c5cff;
  border-color: #7c5cff;
  color: white;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.turn-info {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
  font-weight: 500;
}

.turn-info.my-turn {
  background: #d4edda;
  color: #155724;
}

.turn-info.opponent-turn {
  background: #fff3cd;
  color: #856404;
}

.game-id {
  font-weight: 600;
  color: #0b1320;
}

.game-opponent {
  color: #3f5160;
  font-size: 14px;
}

.game-time {
  color: #9aa4b2;
  font-size: 12px;
}

.game-status {
  color: #7c5cff;
  font-size: 12px;
  font-weight: 500;
}

.score-info {
  color: #9aa4b2;
  font-size: 11px;
  margin-left: 8px;
}

.loading, .empty-state {
  text-align: center;
  padding: 20px;
  color: #9aa4b2;
}

.empty-state-container {
  text-align: center;
  padding: 60px 20px;
  color: #9aa4b2;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state-container h3 {
  color: #3f5160;
  margin: 0 0 8px 0;
}

.empty-state-container p {
  margin: 4px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-view {
    padding: 12px;
  }
}
</style>