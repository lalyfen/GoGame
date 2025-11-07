<template>
  <div class="board-grid">
    <template v-for="rowIndex in size" :key="`row-${rowIndex}`">
      <Intersection
        v-for="colIndex in size"
        :key="`intersection-${rowIndex}-${colIndex}`"
        :row="rowIndex - 1"
        :col="colIndex - 1"
        :is-top-edge="rowIndex === 1"
        :is-bottom-edge="rowIndex === size"
        :is-left-edge="colIndex === 1"
        :is-right-edge="colIndex === size"
        :stone="getStone(rowIndex - 1, colIndex - 1)"
        :is-dead="isDead(rowIndex - 1, colIndex - 1)"
        :is-last-move="isLastMove(rowIndex - 1, colIndex - 1)"
        :territory="getTerritory(rowIndex - 1, colIndex - 1)"
        :show-indicator="showIndicator(rowIndex - 1, colIndex - 1)"
        :current-player="currentPlayer"
        :game-over="gameOver"
        @click="onIntersectionClick"
        @hover="onIntersectionHover"
      >
        <StarPoint v-if="isStarPoint(rowIndex - 1, colIndex - 1)" />
      </Intersection>
    </template>
  </div>
</template>

<script setup>
import Intersection from './Intersection.vue';
import StarPoint from './StarPoint.vue';

const props = defineProps({
  size: {
    type: Number,
    required: true
  },
  board: {
    type: Array,
    required: true
  },
  lastMove: {
    type: Object,
    default: null
  },
  territory: {
    type: Array,
    default: () => []
  },
  deadStones: {
    type: Set,
    default: () => new Set()
  },
  currentPlayer: {
    type: String,
    required: true
  },
  gameOver: {
    type: Boolean,
    default: false
  },
  currentPosition: {
    type: Object,
    default: null
  },
  positionIndicatorEnabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['cellClick', 'cellHover']);

// 星位判断（19路棋盘）
const starPoints = [
  [3, 3], [3, 9], [3, 15],
  [9, 3], [9, 9], [9, 15],
  [15, 3], [15, 9], [15, 15]
];

function isStarPoint(row, col) {
  if (props.size !== 19) return false;
  return starPoints.some(([r, c]) => r === row && c === col);
}

function getStone(row, col) {
  return props.board[row]?.[col] || null;
}

function isDead(row, col) {
  const key = `${row},${col}`;
  return props.deadStones.has(key);
}

function isLastMove(row, col) {
  return props.lastMove && props.lastMove.row === row && props.lastMove.col === col;
}

function getTerritory(row, col) {
  return props.territory[row]?.[col] || null;
}

function showIndicator(row, col) {
  return props.positionIndicatorEnabled && 
         props.currentPosition && 
         props.currentPosition.row === row && 
         props.currentPosition.col === col;
}

function onIntersectionClick(row, col) {
  emit('cellClick', row, col);
}

function onIntersectionHover(row, col) {
  emit('cellHover', row, col);
}
</script>

<style scoped>
.board-grid {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: repeat(v-bind(size), 1fr);
  grid-template-rows: repeat(v-bind(size), 1fr);
  gap: 0;
  position: relative;
  background: #DEB068;
}
</style>
