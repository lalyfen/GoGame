<template>
  <div class="info-panel" ref="infoPanelRef">
    <h2>围棋游戏</h2>

    <div
      class="marking-mode-notice"
      :class="{ active: scoringPhase && markingMode }"
    >
      ⚠️ 标记死子模式：点击棋子标记死子
    </div>

    <CurrentPlayerDisplay
      :current-player="currentPlayer"
      :player-color="playerColor"
      :latest-move-color="latestMoveColor"
      :last-refresh-time="lastRefreshTime"
      :is-my-turn="isMyTurn"
    />

    <ScoreDisplay
      :captures="captures"
      :komi="komi"
      :disabled="scoringPhase || gameOver"
      @updateKomi="$emit('updateKomi', $event)"
    />

    <GameControls
      :game-over="gameOver"
      :scoring-phase="scoringPhase"
      :marking-mode="markingMode"
      @pass="$emit('pass')"
      @endGame="$emit('endGame')"
    />

    <div class="move-count">
      手数：<span>{{ moveCount }}</span>
    </div>

    <PositionControl
      :position-text="positionText"
      @positionKeydown="$emit('positionKeydown', $event)"
      @positionInput="$emit('positionInput', $event)"
      @confirmPosition="$emit('confirmPosition')"
    />
  </div>
</template>

<script setup>
/**
 * 信息面板：使用细粒度组件组合
 */
import CurrentPlayerDisplay from './info/CurrentPlayerDisplay.vue';
import ScoreDisplay from './info/ScoreDisplay.vue';
import GameControls from './info/GameControls.vue';
import PositionControl from './info/PositionControl.vue';

defineProps({
  currentPlayer: { type: String, required: true },
  captures: { type: Object, required: true },
  komi: { type: Number, required: true },
  scoringPhase: { type: Boolean, default: false },
  gameOver: { type: Boolean, default: false },
  markingMode: { type: Boolean, default: false },
  moveCount: { type: Number, required: true },
  positionText: { type: String, required: true },
  // 新增属性
  playerColor: { type: String, default: null },      // 玩家角色
  latestMoveColor: { type: String, default: null },  // 最新落子颜色
  lastRefreshTime: { type: String, default: null },  // 最后刷新时间
  isMyTurn: { type: Boolean, default: null }         // 是否轮到玩家
});

defineEmits([
  'updateKomi',
  'pass',
  'endGame',
  'positionKeydown',
  'positionInput',
  'confirmPosition'
]);
</script>

<style scoped>
.info-panel {
  min-width: 280px;
  width: clamp(280px, 28%, 420px); /* 相对 game-container 的百分比，避免使用视口单位导致挤压 */
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 3%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 2%;
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

/* Webkit浏览器（Chrome, Safari, Edge） */
.info-panel::-webkit-scrollbar {
  width: 6px;
}

.info-panel::-webkit-scrollbar-track {
  background: transparent;
}

.info-panel::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 3px;
  transition: background 0.3s ease;
}

.info-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

/* 仅当鼠标悬停在滚动条区域时才显示轨道/滑块颜色 */
.info-panel::-webkit-scrollbar-track:hover {
  background: rgba(0, 0, 0, 0.06);
}

.info-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.4);
}

.info-panel::-webkit-scrollbar-thumb:active {
  background: rgba(0, 0, 0, 0.6);
}

.info-panel h2 {
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #DEB068;
}

.marking-mode-notice {
  background: #fff3e0;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 15px;
  color: #f57c00;
  display: none;
}

.marking-mode-notice.active {
  display: block;
}

.move-count {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}
</style>
