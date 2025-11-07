<template>
  <div class="app-root">
    <!-- 顶部操作按钮列表（先不接入功能，仅保留接口） -->
    <div class="message-panel-actions">
      <RouterLink to="/logout"><LogoutButton @click="onLogoutClick" /></RouterLink>
      <RouterLink to="/history"><HistoryButton @click="onHistoryClick" /></RouterLink>
      <RouterLink to="/invite"><InviteLinkButton @click="onInviteLinkClick" /></RouterLink>
      <RouterLink to="/messages"><MessageToggleButton @click="onMessageToggleClick" /></RouterLink>
    </div>

    <!-- 使用可调整大小的布局组件 -->
    <ResizableLayout
      :initial-left-width="900"
      :min-left-width="600"
      :min-right-width="280"
      :max-right-width="500"
      :show-resizer="messagePanelVisible"
      @resize="onLayoutResize"
    >
      <!-- 左侧：游戏容器（棋盘 + 控制面板） -->
      <template #left>
        <div class="game-container">
          <Board
            :size="size"
            :board="board"
            :last-move="lastMove"
            :territory="territory"
            :dead-stones="deadStones"
            :current-player="currentPlayer"
            :game-over="gameOver"
            :scoring-phase="scoringPhase"
            :marking-mode="markingMode"
            :position-indicator-enabled="positionIndicatorEnabled"
            :current-position="currentPosition"
            @cellClick="onCellClick"
            @cellHover="onCellHover"
          />

          <InfoPanel
            :current-player="currentPlayer"
            :captures="captures"
            :komi="komi"
            :scoring-phase="scoringPhase"
            :game-over="gameOver"
            :marking-mode="markingMode"
            :move-count="moveCount"
            :position-text="positionText"
            :player-color="gameInfo.playerColor"
            :latest-move-color="gameInfo.latestMoveColor"
            :last-refresh-time="gameInfo.lastRefresh"
            :is-my-turn="gameInfo.isMyTurn"
            @updateKomi="onUpdateKomi"
            @pass="passTurn"
            @endGame="endGame"
            @positionKeydown="onPositionKeydown"
            @positionInput="onPositionInput"
            @confirmPosition="confirmPosition"
          />
        </div>
      </template>

      <!-- 右侧：消息面板 -->
      <template #right>
        <RouterView v-if="messagePanelVisible" />
      </template>
    </ResizableLayout>
  </div>
</template>

<script setup>
/**
 * 根组件：连接组合式逻辑与三个子组件
 * - Board: 纯渲染棋盘，抛出 cellClick/cellHover
 * - InfoPanel: 信息与控制面板
 * - MessagePanel: 消息展示
 * 并实现右侧消息面板宽度拖拽与显示/隐藏
 */
import { ref, computed, onMounted, onUnmounted, provide, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import Board from './components/Board.vue';
import InfoPanel from './components/InfoPanel.vue';
import ResizableLayout from './components/ResizableLayout.vue';
import LogoutButton from './components/actions/LogoutButton.vue';
import HistoryButton from './components/actions/HistoryButton.vue';
import InviteLinkButton from './components/actions/InviteLinkButton.vue';
import MessageToggleButton from './components/actions/MessageToggleButton.vue';
import { useGoGame } from '../shared/composables/useGoGame';
import { useGameStore } from '../stores/gameStore';

// 获取游戏store
const gameStore = useGameStore();

// 获取路由器
const router = useRouter();
const route = useRoute(); // 添加当前路由的访问

// 获取当前游戏ID
const currentGameId = computed(() => gameStore.selectedGameId);

// 邀请ID状态管理 - 暂时设为null，稍后从useGoGame获取
let currentInvitationId = ref(null);

// 获取当前游戏信息
const gameInfo = computed(() => {
  const gameId = currentGameId.value;
  if (!gameId) {
    return {
      playerColor: null,
      latestMoveColor: null,
      lastRefresh: null,
      isMyTurn: null
    };
  }

  const cachedInfo = gameStore.getGameInfoCache(gameId);
  const isMyTurn = gameStore.getIsMyTurn(gameId);

  return {
    playerColor: cachedInfo?.playerColor || null,
    latestMoveColor: cachedInfo?.latestMoveColor || null,
    lastRefresh: cachedInfo?.lastRefresh || null,
    isMyTurn: isMyTurn
  };
});

// 监听store中的当前棋局数据变化
watch(
  () => gameStore.getCurrentGameBoard,
  (newBoard) => {
    if (newBoard && currentGameId.value) {
      console.log('检测到新的棋局数据，更新主棋盘');
      // 使用新的初始化方法从API数据加载游戏
      initializeFromApi(gameStore.getCurrentGameInfo);
    }
  },
  { deep: true }
)

// 监听store中的当前对局信息变化
watch(
  () => gameStore.getCurrentGameInfo,
  (newGameInfo) => {
    if (newGameInfo && currentGameId.value) {
      console.log('检测到新的对局信息:', newGameInfo);
      // 使用新的初始化方法从API数据加载游戏
      initializeFromApi(newGameInfo);
    }
  },
  { deep: true }
)

// 组合式围棋逻辑（无 DOM）
const {
  // 状态
  size,
  board,
  currentPlayer,
  captures,
  komi,
  scoringPhase,
  gameOver,
  markingMode,
  moveCount,
  currentPosition,
  positionIndicatorEnabled,
  lastMove,
  territory,
  deadStones,
  messages,
  currentGameId: goGameCurrentGameId, // 区分命名
  currentInvitationId: goGameInvitationId, // 区分命名
  // 方法
  pushMessage,
  clearMessages,
  positionToString,
  stringToPosition,
  movePosition,
  updateKomi,
  handleMoveAt,
  confirmPosition,
  toggleMarkingMode,
  passTurn,
  confirmScore,
  reset,
  updatePositionFromInput,
  calculateTerritory,
  calculateScore,
  initializeFromApi, // 新增方法
  setGameId, // 新增方法
  setInvitationId, // 新增方法
  getInvitationId, // 新增方法
} = useGoGame(19);

// 将useGoGame中的邀请ID状态赋给本地变量
currentInvitationId = goGameInvitationId;

// 位置展示文本
const positionText = computed(() =>
  positionToString(currentPosition.value.row, currentPosition.value.col)
);

// 事件：棋盘点击/悬浮
function onCellClick(row, col) {
  handleMoveAt(row, col);
}
function onCellHover(row, col) {
  if (!gameOver.value && !scoringPhase.value) {
    currentPosition.value = { row, col };
  }
}

// 事件：信息面板
function onUpdateKomi(val) {
  updateKomi(val);
}

// 结束对局事件处理
async function endGame() {
  if (!currentGameId.value) {
    pushMessage('没有选择对局', 'error');
    return;
  }

  try {
    pushMessage('正在计算得分并结束对局...', 'info');

    const result = await gameStore.endGame(currentGameId.value);

    if (result.success) {
      const { winner, blackScore, whiteScore, details } = result.data;

      // 显示结果信息
      let winnerText = winner === 'black' ? '黑棋获胜' : winner === 'white' ? '白棋获胜' : '平局';
      pushMessage(
        `对局结束！${winnerText}\n黑棋: ${blackScore} 目, 白棋: ${whiteScore} 目`,
        'success'
      );

      // 延迟跳转到历史页面，让用户看到结果
      setTimeout(() => {
        router.push('/history');
      }, 2000);

    } else {
      pushMessage(`结束对局失败: ${result.error.message}`, 'error');
    }
  } catch (error) {
    console.error('结束对局时发生错误:', error);
    pushMessage('结束对局时发生未知错误', 'error');
  }
}
function onPositionKeydown(e) {
  const k = e.key;
  if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter'].includes(k)) {
    e.preventDefault();
  }
  switch (k) {
    case 'ArrowUp':
      movePosition(-1, 0);
      break;
    case 'ArrowDown':
      movePosition(1, 0);
      break;
    case 'ArrowLeft':
      movePosition(0, -1);
      break;
    case 'ArrowRight':
      movePosition(0, 1);
      break;
    case 'Enter':
      confirmPosition();
      break;
  }
}
function onPositionInput(val) {
  updatePositionFromInput(val);
}

// 消息面板显示/隐藏
const messagePanelVisible = ref(true);

function toggleMessagePanel() {
  messagePanelVisible.value = !messagePanelVisible.value;
}

// 顶部操作按钮的占位处理函数（保留接口，暂不实现具体功能）
function onLogoutClick() {}
function onHistoryClick() {}
function onInviteLinkClick() {}
function onMessageToggleClick() {}

// 自动刷新机制
let autoRefreshTimer = null;
const AUTO_REFRESH_INTERVAL = 30 * 1000; // 30秒

// 启动自动刷新
function startAutoRefresh() {
  stopAutoRefresh(); // 清除现有定时器

  if (currentGameId.value) {
    console.log(`启动自动刷新，游戏ID: ${currentGameId.value}`);
    autoRefreshTimer = setInterval(async () => {
      if (currentGameId.value && !gameStore.isRefreshing(currentGameId.value)) {
        console.log('自动刷新游戏信息');
        try {
          await gameStore.refreshGameInfo(currentGameId.value);
        } catch (error) {
          console.error('自动刷新失败:', error);
        }
      }
    }, AUTO_REFRESH_INTERVAL);
  }
}

// 停止自动刷新
function stopAutoRefresh() {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
    console.log('停止自动刷新');
  }
}

// 监听游戏ID变化，重新启动自动刷新
watch(currentGameId, async (newGameId) => {
  console.log('游戏ID发生变化:', newGameId);
  setGameId(newGameId);

  if (newGameId) {
    // 启动自动刷新
    startAutoRefresh();

    // 立即执行一次执棋状态刷新，特别是新游戏时
    console.log('检测到新游戏ID，立即刷新执棋状态信息...');
    try {
      const refreshResult = await gameStore.refreshGameInfo(newGameId);
      if (refreshResult.success) {
        console.log('BoardGame: 新游戏执棋状态立即刷新成功:', refreshResult.data);
      } else {
        console.warn('BoardGame: 新游戏执棋状态立即刷新失败:', refreshResult.error);
      }
    } catch (error) {
      console.error('BoardGame: 立即刷新执棋状态时发生错误:', error);
    }

    // 检查并设置邀请ID
    handleInvitationId(newGameId);
  } else {
    stopAutoRefresh();
    // 清除邀请ID（通过setInvitationId方法）
    setInvitationId(null);
  }
});

// 处理邀请ID逻辑
const handleInvitationId = (gameId) => {
  // 检查URL参数中是否有邀请ID
  if (route.query.invitationId) {
    const invitationId = parseInt(route.query.invitationId);
    console.log(`检测到邀请ID: ${invitationId}, 关联游戏ID: ${gameId}`);

    // 设置当前邀请ID（通过setInvitationId方法）
    setInvitationId(invitationId);

    // 清除URL参数，避免刷新页面时重复处理
    const newQuery = { ...route.query };
    delete newQuery.invitationId;
    router.replace({ query: newQuery });
  } else {
    // 清除邀请ID（通过setInvitationId方法）
    setInvitationId(null);
  }
};

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoRefresh();
  // 移除事件监听器
  window.removeEventListener('moveSuccessful', handleMoveSuccessful);
});

// 处理落子成功事件
function handleMoveSuccessful(event) {
  const { gameId } = event.detail;
  console.log('检测到落子成功，刷新游戏信息:', gameId);

  // 如果是当前游戏，立即刷新
  if (gameId === currentGameId.value) {
    gameStore.refreshGameInfo(gameId);
  }
}

// 应用启动时预加载游戏数据
onMounted(async () => {
  console.log('应用启动，开始预加载游戏数据...')

  try {
    // 预加载未完成对局到内存
    await gameStore.loadIncompleteGames()
    console.log(`预加载完成，加载了 ${gameStore.getIncompleteGames.length} 个对局`)

    // 预加载已完成对局到内存
    await gameStore.loadCompletedGames()
    console.log(`预加载完成，加载了 ${gameStore.getCompletedGames.length} 个已完成对局`)

    // 如果有选中的游戏，加载该游戏数据
    if (currentGameId.value) {
      console.log(`加载选中的游戏: ${currentGameId.value}`);
      await gameStore.loadSelectedGame(currentGameId.value);
      // 启动自动刷新
      startAutoRefresh();
    }
  } catch (error) {
    console.error('预加载游戏数据失败:', error)
  }

  if (!messages.value.length) {
    pushMessage('欢迎来到围棋游戏！黑棋先行。', 'info');
  }

  // 添加事件监听器
  window.addEventListener('moveSuccessful', handleMoveSuccessful);
});

// 监听游戏ID变化，更新useGoGame的游戏ID (已移除到上面的统一watch中)
// watch(currentGameId, (newGameId) => {
//   console.log('游戏ID发生变化:', newGameId);
//   setGameId(newGameId);
// });

// 提供消息数据与接口给路由视图使用
provide('messages', messages);
provide('clearMessages', clearMessages);
</script>

<style>
/* 全局样式已在 src/main.js 通过 ./assets/temp.css 引入 */
</style>
