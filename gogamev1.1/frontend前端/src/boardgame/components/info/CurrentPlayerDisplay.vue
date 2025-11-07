<template>
  <div class="current-player-info">
    <!-- 玩家角色信息 -->
    <div v-if="playerColor" class="player-role">
      <div class="role-title">您的角色：</div>
      <div class="role-content">
        <div class="player-stone" :class="playerColor"></div>
        <span>{{ playerColor === 'black' ? '黑棋' : '白棋' }}</span>
      </div>
    </div>

    <!-- 轮次信息 -->
    <div v-if="playerColor && isMyTurn !== null" class="turn-status">
      <div class="turn-title" :class="isMyTurn ? 'my-turn' : 'opponent-turn'">
        {{ isMyTurn ? '轮到您落子' : '等待对手落子' }}
      </div>
      <div v-if="latestMoveColor" class="latest-move">
        最新落子：
        <div class="player-stone small" :class="latestMoveColor"></div>
        <span>{{ latestMoveColor === 'black' ? '黑棋' : '白棋' }}</span>
      </div>
    </div>

    <!-- 传统当前玩家显示（作为后备） -->
    <div v-if="!playerColor" class="current-player">
      <span>当前玩家：</span>
      <div class="player-stone" :class="currentPlayer"></div>
      <span>{{ currentPlayer === 'black' ? '黑棋' : '白棋' }}</span>
    </div>

    <!-- 最后刷新时间 -->
    <div v-if="lastRefreshTime" class="refresh-info">
      <span class="refresh-time">最后更新：{{ formatRefreshTime(lastRefreshTime) }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentPlayer: {
    type: String,
    required: true,
    validator: (value) => ['black', 'white'].includes(value)
  },
  // 新增属性
  playerColor: { type: String, default: null },      // 玩家角色
  latestMoveColor: { type: String, default: null },  // 最新落子颜色
  lastRefreshTime: { type: String, default: null },  // 最后刷新时间
  isMyTurn: { type: Boolean, default: null }         // 是否轮到玩家
});

// 格式化刷新时间
const formatRefreshTime = (timeStr) => {
  if (!timeStr) return ''

  try {
    const date = new Date(timeStr)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) {
      return '刚刚'
    } else if (diffMins < 60) {
      return `${diffMins}分钟前`
    } else if (diffMins < 1440) { // 24小时
      const hours = Math.floor(diffMins / 60)
      return `${hours}小时前`
    } else {
      // 超过24小时显示具体时间
      return date.toLocaleString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  } catch (error) {
    console.error('时间格式化错误:', error)
    return '未知时间'
  }
}
</script>

<style scoped>
.current-player-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.player-role {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.role-title {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.role-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.turn-status {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid;
}

.turn-status.my-turn {
  background: #d4edda;
  border-left-color: #28a745;
}

.turn-status.opponent-turn {
  background: #fff3cd;
  border-left-color: #ffc107;
}

.turn-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.turn-status.my-turn .turn-title {
  color: #155724;
}

.turn-status.opponent-turn .turn-title {
  color: #856404;
}

.latest-move {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.refresh-info {
  text-align: center;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.refresh-time {
  font-size: 12px;
  color: #999;
}

.current-player {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
}

.player-stone {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  box-shadow: 1px 1px 3px rgba(0,0,0,0.3);
}

.player-stone.small {
  width: 20px;
  height: 20px;
  box-shadow: 0.5px 0.5px 2px rgba(0,0,0,0.3);
}

.player-stone.black {
  background: radial-gradient(circle at 30% 30%, #555, #000);
}

.player-stone.white {
  background: radial-gradient(circle at 30% 30%, #fff, #e0e0e0);
  border: 1px solid #999;
}
</style>
