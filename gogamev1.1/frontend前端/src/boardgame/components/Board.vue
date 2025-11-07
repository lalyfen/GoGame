<template>
  <div class="board-container">
    <BoardLabels :size="size" />
    <BoardGrid
      :size="size"
      :board="board"
      :last-move="lastMove"
      :territory="territory"
      :dead-stones="deadStones"
      :current-player="currentPlayer"
      :game-over="gameOver"
      :current-position="currentPosition"
      :position-indicator-enabled="positionIndicatorEnabled"
      @cellClick="onCellClick"
      @cellHover="onCellHover"
    />
  </div>
</template>

<script setup>
/**
 * 棋盘组件（纯渲染/事件发射）
 * 使用细粒度子组件：BoardLabels, BoardGrid
 */
import BoardLabels from './board/BoardLabels.vue';
import BoardGrid from './board/BoardGrid.vue';

defineProps({
  size: { type: Number, default: 19 },
  board: { type: Array, required: true },
  lastMove: { type: Object, default: null },
  territory: { type: Array, required: true },
  deadStones: { type: Object, required: true },
  currentPlayer: { type: String, required: true },
  gameOver: { type: Boolean, default: false },
  scoringPhase: { type: Boolean, default: false },
  markingMode: { type: Boolean, default: false },
  positionIndicatorEnabled: { type: Boolean, default: true },
  currentPosition: { type: Object, required: true }
});

const emit = defineEmits(['cellClick', 'cellHover']);

function onCellClick(row, col) {
  emit('cellClick', row, col);
}

function onCellHover(row, col) {
  emit('cellHover', row, col);
}
</script>

<style>
/* 使用全局样式（src/assets/temp.css），此处不定义 scoped 样式 */
</style>
